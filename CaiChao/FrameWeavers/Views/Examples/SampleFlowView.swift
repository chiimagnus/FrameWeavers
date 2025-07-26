import SwiftUI

/// 示例流程视图 - 复用现有的SelectStyleView和ProcessingView
struct SampleFlowView: View {
    @Environment(\.dismiss) private var dismiss
    let comicResult: ComicResult

    @State private var currentStep: FlowStep = .styleSelection
    @State private var navigateToProcessing = false
    @State private var navigateToResults = false
    @StateObject private var mockViewModel: MockVideoUploadViewModel

    init(comicResult: ComicResult) {
        self.comicResult = comicResult
        self._mockViewModel = StateObject(wrappedValue: MockVideoUploadViewModel(comicResult: comicResult))
    }

    enum FlowStep {
        case styleSelection
        case processing
        case results
    }

    var body: some View {
        NavigationStack {
            Group {
                switch currentStep {
                case .styleSelection:
                    SelectStyleView(viewModel: mockViewModel)
                        .onAppear {
                            // 设置一些模拟视频数据
                            mockViewModel.selectVideos([
                                URL(string: "file:///mock/sample1.mp4")!,
                                URL(string: "file:///mock/sample2.mp4")!
                            ])
                        }
                        .onChange(of: mockViewModel.uploadStatus) { _, newStatus in
                            if newStatus == .uploading || newStatus == .processing {
                                withAnimation {
                                    currentStep = .processing
                                }
                            }
                        }
                case .processing:
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

}

// MARK: - Mock ViewModel
class MockVideoUploadViewModel: VideoUploadViewModel {
    private let targetComicResult: ComicResult?

    init(comicResult: ComicResult? = nil) {
        self.targetComicResult = comicResult
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
                    // 设置目标结果
                    if let result = self.targetComicResult {
                        self.comicResult = result
                    }
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
