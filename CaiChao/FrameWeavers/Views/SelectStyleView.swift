import SwiftUI

struct SelectStyleView: View {
    @Environment(\.dismiss) private var dismiss
    @ObservedObject var viewModel: VideoUploadViewModel
    @State private var selectedStyle: String = ""
    @State private var navigateToProcessing = false
    
    // 定义故事风格
    private let storyStyles = [
        ("文艺哲学", "文艺\n哲学"),
        ("童话想象", "童话\n想象"),
        ("悬念反转", "悬念\n反转"),
        ("生活散文", "生活\n散文")
    ]
    
    var body: some View {
        NavigationStack {
            ZStack {
                Image("背景单色")
                    .resizable()
                    .scaledToFill()
                    .ignoresSafeArea()

                VStack(spacing: 30) {
                    Text("· 选择故事风格 ·")
                        .font(.custom("STKaiti", size: 16))
                        .fontWeight(.bold)
                        .foregroundColor(Color(hex: "#2F2617"))
                        .padding(.bottom, 50)
                    
                    ZStack {
                        Image("四象限")
                            .resizable()
                            .scaledToFill()
                            .frame(width: 400, height: 400)
                        
                        // 图钉图标 - 初始在右上角，根据选中位置移动
                        let pinPositions = [
                            (x: 180, y: 40),   // 左上象限右上角
                            (x: 370, y: 40),   // 右上象限右上角（初始位置）
                            (x: 180, y: 220),  // 左下象限右上角
                            (x: 370, y: 220)   // 右下象限右上角
                        ]
                        
                        let pinIndex = selectedStyle.isEmpty ? 1 : (storyStyles.firstIndex { $0.0 == selectedStyle } ?? 1)
                        Image("图钉")
                            .resizable()
                            .scaledToFit()
                            .frame(width: 60, height: 60)
                            .position(x: CGFloat(pinPositions[pinIndex].x), y: CGFloat(pinPositions[pinIndex].y))
                        
                        // 四个象限的风格选择按钮
                        let positions = [
                            (x: 100, y: 100),  // 左上
                            (x: 300, y: 100),  // 右上
                            (x: 100, y: 300),  // 左下
                            (x: 300, y: 300)   // 右下
                        ]
                        
                        ForEach(Array(storyStyles.enumerated()), id: \.offset) { index, style in
                            let styleKey = style.0
                            let styleText = style.1
                            
                            Button(action: {
                                selectedStyle = styleKey
                            }) {
                                Text(styleText)
                                    .font(.custom("STKaiti", size: 24))
                                    .fontWeight(.bold)
                                    .foregroundColor(selectedStyle == styleKey ? Color(hex: "#FF6B35") : Color(hex: "#855C23"))
                            }
                            .position(x: CGFloat(positions[index].x), y: CGFloat(positions[index].y))
                        }
                    }
                    .frame(width: 400, height: 400)
                    .padding(.horizontal)
                    .padding(.bottom, 100)

                    // 开始生成按钮
                    Button(action: {
                        startGeneration()
                    }) {
                        ZStack {
                            Image("翻开画册")
                                .resizable()
                                .aspectRatio(contentMode: .fit)
                                .frame(width: 250, height: 44)

                            Text("开始生成")
                                .font(.custom("STKaiti", size: 24))
                                .fontWeight(.bold)
                                .foregroundColor(
                                    selectedStyle.isEmpty ?
                                        Color(hex: "#CCCCCC") :
                                        Color(hex: "#855C23")
                                )
                        }
                    }
                    .disabled(selectedStyle.isEmpty)
                    .opacity(selectedStyle.isEmpty ? 0.6 : 1.0)
                    
                    // // 显示已选择的视频数量
                    // Text("已选择 \(viewModel.selectedVideos.count) 个视频")
                    //     .font(.custom("STKaiti", size: 14))
                    //     .foregroundColor(Color(hex: "#2F2617"))
                    
                    // // 调试信息
                    // Text("状态: \(viewModel.uploadStatus.rawValue)")
                    //     .font(.caption)
                    //     .foregroundColor(.gray)
                }
            }
            .navigationDestination(isPresented: $navigateToProcessing) {
                ProcessingView(viewModel: viewModel)
            }
            .navigationBarBackButtonHidden(true)
            .toolbar {
                ToolbarItem(placement: .navigationBarLeading) {
                    Button(action: {
                        dismiss()
                    }) {
                        Image(systemName: "chevron.left")
                            .foregroundColor(Color(hex: "#2F2617"))
                    }
                }
            }
        }
        .onAppear {
            print("SelectStyleView: 已选择 \(viewModel.selectedVideos.count) 个视频")
            print("SelectStyleView: 初始状态 \(viewModel.uploadStatus.rawValue)")
        }
    }
    
    private func startGeneration() {
        guard !selectedStyle.isEmpty else { return }
        
        print("开始生成按钮被点击")
        print("当前状态: \(viewModel.uploadStatus.rawValue)")
        print("视频数量: \(viewModel.selectedVideos.count)")
        
        // 确保状态正确
        viewModel.uploadStatus = .pending
        viewModel.uploadProgress = 0
        
        // 触发上传和处理流程
        viewModel.uploadVideo()
        
        // 导航到处理视图
        navigateToProcessing = true
    }
}

// MARK: - SwiftUI Preview
struct SelectStyleView_Previews: PreviewProvider {
    static var previews: some View {
        let viewModel = VideoUploadViewModel()
        viewModel.selectVideos([
            URL(string: "file:///mock/video1.mp4")!,
            URL(string: "file:///mock/video2.mp4")!
        ])
        return SelectStyleView(viewModel: viewModel)
    }
}
