import SwiftUI

/// 打字机效果视图组件
/// 支持逐字符显示文本动画，可配置打字速度
struct TypewriterView: View {
    // MARK: - 输入参数
    let fullText: String
    let typeSpeed: TimeInterval
    let showCursor: Bool
    let onComplete: (() -> Void)?

    // MARK: - 状态变量
    @State private var displayedText: String = ""
    @State private var currentIndex: Int = 0
    @State private var isAnimating: Bool = false
    @State private var showCursorBlink: Bool = true
    @State private var animationTimer: Timer?
    @State private var cursorTimer: Timer?

    // MARK: - 初始化器
    init(text: String,
         typeSpeed: TimeInterval = 0.05,
         showCursor: Bool = false,
         onComplete: (() -> Void)? = nil) {
        self.fullText = text
        self.typeSpeed = typeSpeed
        self.showCursor = showCursor
        self.onComplete = onComplete
    }
    
    var body: some View {
        HStack(spacing: 0) {
            Text(displayedText)

            if showCursor {
                Text("|")
                    .opacity(showCursorBlink ? 1 : 0)
                    .animation(.easeInOut(duration: 0.5).repeatForever(autoreverses: true), value: showCursorBlink)
            }
        }
        .onAppear {
            startTypewriterAnimation()
            if showCursor {
                startCursorBlinking()
            }
        }
        .onDisappear {
            stopTypewriterAnimation()
        }
    }
    
    // MARK: - 动画控制方法
    private func startTypewriterAnimation() {
        // 重置状态
        displayedText = ""
        currentIndex = 0
        isAnimating = true

        // 启动动画
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
        cursorTimer = Timer.scheduledTimer(withTimeInterval: 0.5, repeats: true) { _ in
            showCursorBlink.toggle()
        }
    }

    private func typeNextCharacter() {
        guard isAnimating, currentIndex < fullText.count else {
            // 动画完成
            isAnimating = false
            if showCursor {
                cursorTimer?.invalidate()
                showCursorBlink = true // 保持光标显示
            }
            onComplete?()
            return
        }

        let index = fullText.index(fullText.startIndex, offsetBy: currentIndex)
        displayedText.append(fullText[index])
        currentIndex += 1

        // 使用 Timer 替代 DispatchQueue 以便更好的控制
        animationTimer = Timer.scheduledTimer(withTimeInterval: typeSpeed, repeats: false) { _ in
            typeNextCharacter()
        }
    }

    // MARK: - 公共控制方法
    /// 暂停打字动画
    func pause() {
        animationTimer?.invalidate()
        animationTimer = nil
    }

    /// 继续打字动画
    func resume() {
        guard isAnimating else { return }
        typeNextCharacter()
    }

    /// 重新开始动画
    func restart() {
        stopTypewriterAnimation()
        startTypewriterAnimation()
        if showCursor {
            startCursorBlinking()
        }
    }

    /// 立即完成动画
    func complete() {
        stopTypewriterAnimation()
        displayedText = fullText
        currentIndex = fullText.count
        onComplete?()
    }
}

// // MARK: - 预览
// struct TypewriterView_Previews: PreviewProvider {
//     static var previews: some View {
//         TypewriterView(
//             text: """
//             有些记忆，
//             沉在手机深处，
//             无人翻阅，也无人倾听。
//             我们捡起那些画面，
//             像织布的人，
//             一帧帧织成故事。
//             """,
//             typeSpeed: 0.08
//         )
//         .font(.custom("STKaiti", size: 16))
//         .fontWeight(.bold)
//         .multilineTextAlignment(.center)
//         .foregroundColor(Color(hex: "#2F2617"))
//         .lineSpacing(15)
//         .padding()
//     }
// }