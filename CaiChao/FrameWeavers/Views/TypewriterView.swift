import SwiftUI

/// 打字机效果视图组件
/// 支持逐字符显示文本动画，可配置打字速度
struct TypewriterView: View {
    // MARK: - 输入参数
    let fullText: String
    let typeSpeed: TimeInterval
    
    // MARK: - 状态变量
    @State private var displayedText: String = ""
    @State private var currentIndex: Int = 0
    @State private var isAnimating: Bool = false
    
    // MARK: - 初始化器
    init(text: String, typeSpeed: TimeInterval = 0.05) {
        self.fullText = text
        self.typeSpeed = typeSpeed
    }
    
    var body: some View {
        Text(displayedText)
            .onAppear {
                startTypewriterAnimation()
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
    }
    
    private func typeNextCharacter() {
        guard isAnimating, currentIndex < fullText.count else {
            return
        }
        
        let index = fullText.index(fullText.startIndex, offsetBy: currentIndex)
        displayedText.append(fullText[index])
        currentIndex += 1
        
        // 递归调用下一字符
        DispatchQueue.main.asyncAfter(deadline: .now() + typeSpeed) {
            typeNextCharacter()
        }
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
//         .font(.custom("Kaiti SC", size: 16))
//         .fontWeight(.bold)
//         .multilineTextAlignment(.center)
//         .foregroundColor(Color(hex: "#2F2617"))
//         .lineSpacing(15)
//         .padding()
//     }
// }