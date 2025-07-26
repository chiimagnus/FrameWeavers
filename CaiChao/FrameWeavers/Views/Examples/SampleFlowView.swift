import SwiftUI

/// 示例流程视图 - 模拟完整的风格选择和处理流程
struct SampleFlowView: View {
    @Environment(\.dismiss) private var dismiss
    let comicResult: ComicResult
    
    @State private var currentStep: FlowStep = .styleSelection
    @State private var selectedStyle: String = ""
    @State private var showProcessing = false
    @StateObject private var mockViewModel = MockVideoUploadViewModel()
    
    enum FlowStep {
        case styleSelection
        case processing
        case results
    }
    
    // 定义故事风格
    private let storyStyles = [
        ("文艺哲学", "文 艺\n哲 学"),
        ("童话想象", "童 话\n想 象"),
        ("悬念反转", "悬 念\n反 转"),
        ("生活散文", "生 活\n散 文")
    ]
    
    var body: some View {
        NavigationStack {
            Group {
                switch currentStep {
                case .styleSelection:
                    styleSelectionView
                case .processing:
                    processingView
                case .results:
                    OpenResultsView(comicResult: comicResult)
                }
            }
            .navigationBarBackButtonHidden(true)
            .toolbar {
                ToolbarItem(placement: .navigationBarLeading) {
                    Button(action: {
                        if currentStep == .styleSelection {
                            dismiss()
                        } else {
                            // 返回上一步
                            withAnimation {
                                if currentStep == .processing {
                                    currentStep = .styleSelection
                                    mockViewModel.reset()
                                } else if currentStep == .results {
                                    currentStep = .processing
                                }
                            }
                        }
                    }) {
                        Image(systemName: "chevron.left")
                            .foregroundColor(Color(hex: "#2F2617"))
                    }
                }
            }
        }
    }
    
    // MARK: - 风格选择视图
    private var styleSelectionView: some View {
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

                // 风格选择网格
                LazyVGrid(columns: Array(repeating: GridItem(.flexible(), spacing: 20), count: 2), spacing: 20) {
                    ForEach(storyStyles, id: \.0) { style in
                        Button(action: {
                            selectedStyle = style.0
                        }) {
                            VStack(spacing: 10) {
                                Text(style.1)
                                    .font(.custom("WSQuanXing", size: 20))
                                    .fontWeight(.bold)
                                    .foregroundColor(
                                        selectedStyle == style.0 ?
                                            Color(hex: "#855C23") :
                                            Color(hex: "#2F2617")
                                    )
                                    .multilineTextAlignment(.center)
                                    .lineSpacing(5)
                            }
                            .frame(width: 150, height: 150)
                            .background(
                                RoundedRectangle(cornerRadius: 20)
                                    .fill(Color.white.opacity(0.8))
                                    .overlay(
                                        RoundedRectangle(cornerRadius: 20)
                                            .stroke(
                                                selectedStyle == style.0 ?
                                                    Color(hex: "#855C23") :
                                                    Color.clear,
                                                lineWidth: 3
                                            )
                                    )
                            )
                        }
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
                            .font(.custom("WSQuanXing", size: 24))
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
            }
        }
    }
    
    // MARK: - 处理视图
    private var processingView: some View {
        ProcessingView(viewModel: mockViewModel)
            .onAppear {
                mockViewModel.startMockProcessing()
            }
            .onChange(of: mockViewModel.uploadStatus) { _, newStatus in
                if newStatus == .completed {
                    DispatchQueue.main.asyncAfter(deadline: .now() + 1) {
                        withAnimation {
                            currentStep = .results
                        }
                    }
                }
            }
    }
    
    private func startGeneration() {
        guard !selectedStyle.isEmpty else { return }
        
        withAnimation {
            currentStep = .processing
        }
    }
}

// MARK: - Mock ViewModel
class MockVideoUploadViewModel: VideoUploadViewModel {
    
    override init() {
        super.init()
        // 设置一些模拟视频
        self.selectedVideos = [
            URL(string: "file:///mock/sample1.mp4")!,
            URL(string: "file:///mock/sample2.mp4")!
        ]
    }
    
    func startMockProcessing() {
        uploadStatus = .uploading
        uploadProgress = 0
        
        // 模拟上传进度
        Timer.scheduledTimer(withTimeInterval: 0.1, repeats: true) { timer in
            DispatchQueue.main.async {
                self.uploadProgress += 0.02
                
                if self.uploadProgress >= 0.3 {
                    self.uploadStatus = .processing
                }
                
                if self.uploadProgress >= 1.0 {
                    self.uploadProgress = 1.0
                    self.uploadStatus = .completed
                    timer.invalidate()
                }
            }
        }
    }
    
    override func reset() {
        super.reset()
        uploadStatus = .pending
        uploadProgress = 0
        errorMessage = nil
    }
}

#Preview {
    SampleFlowView(comicResult: ComicResult(
        comicId: "preview-001",
        deviceId: "preview-device",
        originalVideoTitle: "预览视频",
        creationDate: "2025-07-26",
        panelCount: 3,
        panels: [
            ComicPanel(
                panelNumber: 1,
                imageUrl: "Image1",
                narration: "在一个阳光明媚的早晨，小明背着书包走在上学的路上。"
            ),
            ComicPanel(
                panelNumber: 2,
                imageUrl: "Image2",
                narration: "突然，一只可爱的小狗从草丛中跳了出来。"
            ),
            ComicPanel(
                panelNumber: 3,
                imageUrl: "Image3",
                narration: "小明决定带着这只小狗一起回家。"
            )
        ],
        finalQuestions: [
            "你觉得小明为什么会选择这个名字？",
            "如果你是小明，你会如何处理？"
        ]
    ))
}
