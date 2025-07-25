import SwiftUI

/// 打字机效果演示视图
/// 展示不同配置的打字机效果
struct TypewriterDemoView: View {
    @State private var currentDemo = 0
    @State private var isPlaying = false
    
    let demoTexts = [
        "欢迎来到帧织者的世界。",
        "在这里，每一帧都是故事的片段。",
        "我们用技术编织回忆，让时光重新流淌。",
        "这是一个更长的文本示例，用来展示打字机效果在处理较长内容时的表现。它包含了多个句子，以及不同的标点符号！你觉得效果如何？"
    ]
    
    var body: some View {
        NavigationView {
            ScrollView {
                VStack(spacing: 30) {
                    // 标题
                    Text("打字机效果演示")
                        .font(.largeTitle)
                        .fontWeight(.bold)
                        .padding()
                    
                    // 基础效果
                    demoSection(
                        title: "基础效果",
                        description: "简单的逐字符显示"
                    ) {
                        TypewriterView(
                            text: demoTexts[0],
                            typeSpeed: 0.08
                        )
                        .font(.title2)
                        .foregroundColor(.primary)
                    }
                    
                    // 带光标效果
                    demoSection(
                        title: "带光标效果",
                        description: "显示闪烁的光标"
                    ) {
                        TypewriterView(
                            text: demoTexts[1],
                            typeSpeed: 0.06,
                            showCursor: true
                        )
                        .font(.title2)
                        .foregroundColor(.blue)
                    }
                    
                    // 高级效果 - 戏剧性
                    demoSection(
                        title: "戏剧性效果",
                        description: "可变速度 + 渐入动画"
                    ) {
                        AdvancedTypewriterView(
                            text: demoTexts[2],
                            config: .dramatic,
                            onComplete: {
                                print("戏剧性效果完成")
                            }
                        )
                        .font(.title2)
                        .foregroundColor(.purple)
                    }
                    
                    // 快速效果
                    demoSection(
                        title: "快速效果",
                        description: "高速打字，适合长文本"
                    ) {
                        AdvancedTypewriterView(
                            text: demoTexts[3],
                            config: .fast,
                            onCharacterTyped: { character in
                                // 可以在这里添加音效
                                if character == "！" || character == "？" {
                                    print("特殊字符: \(character)")
                                }
                            }
                        )
                        .font(.body)
                        .foregroundColor(.green)
                    }
                    
                    // 自定义配置示例
                    demoSection(
                        title: "自定义配置",
                        description: "慢速 + 无光标 + 渐入效果"
                    ) {
                        AdvancedTypewriterView(
                            text: "这是一个自定义配置的示例，展示了灵活的配置选项。",
                            config: AdvancedTypewriterView.Configuration(
                                typeSpeed: 0.12,
                                showCursor: false,
                                fadeInEffect: true,
                                characterDelay: 0.3
                            )
                        )
                        .font(.title3)
                        .foregroundColor(.orange)
                    }
                    
                    // 控制按钮
                    controlButtons()
                }
                .padding()
            }
            .navigationTitle("打字机效果")
            .navigationBarTitleDisplayMode(.inline)
        }
    }
    
    @ViewBuilder
    private func demoSection<Content: View>(
        title: String,
        description: String,
        @ViewBuilder content: () -> Content
    ) -> some View {
        VStack(alignment: .leading, spacing: 12) {
            VStack(alignment: .leading, spacing: 4) {
                Text(title)
                    .font(.headline)
                    .fontWeight(.semibold)
                
                Text(description)
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
            
            content()
                .padding()
                .background(Color.gray.opacity(0.1))
                .cornerRadius(12)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
    }
    
    @ViewBuilder
    private func controlButtons() -> some View {
        VStack(spacing: 16) {
            Text("使用建议")
                .font(.headline)
                .fontWeight(.semibold)
            
            VStack(alignment: .leading, spacing: 8) {
                Text("• 短文本使用基础效果，速度 0.05-0.08 秒")
                Text("• 长文本使用快速效果，速度 0.02-0.03 秒")
                Text("• 重要内容使用戏剧性效果增强表现力")
                Text("• 可以通过 onComplete 回调处理动画完成事件")
                Text("• 支持暂停、继续、重启等控制方法")
            }
            .font(.caption)
            .foregroundColor(.secondary)
            .padding()
            .background(Color.blue.opacity(0.1))
            .cornerRadius(8)
        }
    }
}

#Preview {
    TypewriterDemoView()
}
