import SwiftUI

/// 高级打字机效果视图组件
/// 支持多种动画效果、音效、可变速度等高级功能
struct AdvancedTypewriterView: View {
    // MARK: - 配置结构
    struct Configuration {
        var typeSpeed: TimeInterval = 0.05
        var showCursor: Bool = true
        var cursorBlinkSpeed: TimeInterval = 0.5
        var enableSound: Bool = false
        var variableSpeed: Bool = false // 标点符号处暂停更久
        var fadeInEffect: Bool = false
        var characterDelay: TimeInterval = 0.02
        
        static let `default` = Configuration()
        static let fast = Configuration(typeSpeed: 0.02, cursorBlinkSpeed: 0.3)
        static let slow = Configuration(typeSpeed: 0.1, cursorBlinkSpeed: 0.8)
        static let dramatic = Configuration(
            typeSpeed: 0.08,
            showCursor: true,
            variableSpeed: true,
            fadeInEffect: true
        )
    }
    
    // MARK: - 输入参数
    let fullText: String
    let config: Configuration
    let onComplete: (() -> Void)?
    let onCharacterTyped: ((Character) -> Void)?
    
    // MARK: - 状态变量
    @State private var displayedText: String = ""
    @State private var currentIndex: Int = 0
    @State private var isAnimating: Bool = false
    @State private var showCursorBlink: Bool = true
    @State private var animationTimer: Timer?
    @State private var cursorTimer: Timer?
    @State private var characterOpacities: [Double] = []
    
    // MARK: - 初始化器
    init(text: String, 
         config: Configuration = .default,
         onComplete: (() -> Void)? = nil,
         onCharacterTyped: ((Character) -> Void)? = nil) {
        self.fullText = text
        self.config = config
        self.onComplete = onComplete
        self.onCharacterTyped = onCharacterTyped
    }
    
    var body: some View {
        HStack(spacing: 0) {
            if config.fadeInEffect {
                // 渐入效果的文本显示
                HStack(spacing: 0) {
                    ForEach(Array(displayedText.enumerated()), id: \.offset) { index, character in
                        Text(String(character))
                            .opacity(index < characterOpacities.count ? characterOpacities[index] : 0)
                    }
                }
            } else {
                Text(displayedText)
            }
            
            if config.showCursor {
                Text("|")
                    .opacity(showCursorBlink ? 1 : 0)
                    .animation(.easeInOut(duration: config.cursorBlinkSpeed).repeatForever(autoreverses: true), 
                              value: showCursorBlink)
            }
        }
        .onAppear {
            startTypewriterAnimation()
            if config.showCursor {
                startCursorBlinking()
            }
        }
        .onDisappear {
            stopTypewriterAnimation()
        }
    }
    
    // MARK: - 动画控制方法
    private func startTypewriterAnimation() {
        displayedText = ""
        currentIndex = 0
        isAnimating = true
        characterOpacities = []
        
        typeNextCharacter()
    }
    
    private func stopTypewriterAnimation() {
        isAnimating = false
        animationTimer?.invalidate()
        animationTimer = nil
        cursorTimer?.invalidate()
        cursorTimer = nil
    }
    
    private func startCursorBlinking() {
        cursorTimer = Timer.scheduledTimer(withTimeInterval: config.cursorBlinkSpeed, repeats: true) { _ in
            showCursorBlink.toggle()
        }
    }
    
    private func typeNextCharacter() {
        guard isAnimating, currentIndex < fullText.count else {
            // 动画完成
            isAnimating = false
            if config.showCursor {
                cursorTimer?.invalidate()
                showCursorBlink = true
            }
            onComplete?()
            return
        }
        
        let index = fullText.index(fullText.startIndex, offsetBy: currentIndex)
        let character = fullText[index]
        
        displayedText.append(character)
        
        // 渐入效果
        if config.fadeInEffect {
            characterOpacities.append(0)
            withAnimation(.easeIn(duration: config.characterDelay)) {
                if characterOpacities.count > 0 {
                    characterOpacities[characterOpacities.count - 1] = 1.0
                }
            }
        }
        
        currentIndex += 1
        onCharacterTyped?(character)
        
        // 可变速度：标点符号处暂停更久
        let delay = config.variableSpeed ? getDelayForCharacter(character) : config.typeSpeed
        
        animationTimer = Timer.scheduledTimer(withTimeInterval: delay, repeats: false) { _ in
            typeNextCharacter()
        }
    }
    
    private func getDelayForCharacter(_ character: Character) -> TimeInterval {
        switch character {
        case ".", "!", "?":
            return config.typeSpeed * 3 // 句号等暂停3倍时间
        case ",", ";", ":":
            return config.typeSpeed * 2 // 逗号等暂停2倍时间
        case "\n":
            return config.typeSpeed * 2 // 换行暂停2倍时间
        default:
            return config.typeSpeed
        }
    }
    
    // MARK: - 公共控制方法
    func pause() {
        animationTimer?.invalidate()
        animationTimer = nil
    }
    
    func resume() {
        guard isAnimating else { return }
        typeNextCharacter()
    }
    
    func restart() {
        stopTypewriterAnimation()
        startTypewriterAnimation()
        if config.showCursor {
            startCursorBlinking()
        }
    }
    
    func complete() {
        stopTypewriterAnimation()
        displayedText = fullText
        currentIndex = fullText.count
        
        if config.fadeInEffect {
            characterOpacities = Array(repeating: 1.0, count: fullText.count)
        }
        
        onComplete?()
    }
}

// MARK: - 预览
#Preview {
    VStack(spacing: 30) {
        AdvancedTypewriterView(
            text: "这是一个基础的打字机效果。",
            config: .default
        )
        .font(.title2)
        .padding()
        
        AdvancedTypewriterView(
            text: "这是一个戏剧性的效果，包含可变速度和渐入动画！",
            config: .dramatic
        )
        .font(.title2)
        .foregroundColor(.blue)
        .padding()
    }
}
