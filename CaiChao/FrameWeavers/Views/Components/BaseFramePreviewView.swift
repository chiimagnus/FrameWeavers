import SwiftUI

// MARK: - 基础帧预览视图
struct BaseFramePreviewView: View {
    let baseFrames: [BaseFrameData]
    @StateObject private var previewVM = BaseFramePreviewViewModel()
    
    var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            headerView
            
            if baseFrames.isEmpty {
                emptyStateView
            } else {
                framesGridView
            }
        }
        .padding()
        .background(Color(.systemBackground))
        .cornerRadius(12)
        .shadow(radius: 2)
    }
    
    // MARK: - 头部视图
    private var headerView: some View {
        HStack {
            Label("基础帧预览", systemImage: "photo.on.rectangle")
                .font(.headline)
            
            Spacer()
            
            Text("\(baseFrames.count) 帧")
                .font(.subheadline)
                .foregroundColor(.secondary)
        }
    }
    
    // MARK: - 空状态视图
    private var emptyStateView: some View {
        VStack(spacing: 12) {
            Image(systemName: "photo")
                .font(.largeTitle)
                .foregroundColor(.secondary)
            
            Text("暂无基础帧")
                .font(.body)
                .foregroundColor(.secondary)
        }
        .frame(maxWidth: .infinity)
        .padding(.vertical, 40)
    }
    
    // MARK: - 网格视图
    private var framesGridView: some View {
        ScrollView(.horizontal, showsIndicators: false) {
            LazyHStack(spacing: 12) {
                ForEach(baseFrames) { frame in
                    BaseFrameThumbnailView(frame: frame)
                        .onTapGesture {
                            previewVM.selectFrame(frame)
                        }
                }
            }
            .padding(.horizontal, 4)
        }
        .frame(height: 120)
        .sheet(item: $previewVM.selectedFrame) { frame in
            BaseFrameDetailView(frame: frame, isZoomed: $previewVM.isZoomed)
        }
    }
}

// MARK: - 基础帧缩略图视图
struct BaseFrameThumbnailView: View {
    let frame: BaseFrameData
    
    var body: some View {
        VStack(spacing: 4) {
            AsyncImage(url: frame.thumbnailURL) { phase in
                switch phase {
                case .empty:
                    ProgressView()
                        .frame(width: 80, height: 60)
                case .success(let image):
                    image
                        .resizable()
                        .aspectRatio(contentMode: .fill)
                        .frame(width: 80, height: 60)
                        .clipped()
                        .cornerRadius(8)
                case .failure:
                    Image(systemName: "photo")
                        .font(.title2)
                        .foregroundColor(.secondary)
                        .frame(width: 80, height: 60)
                        .background(Color(.systemGray5))
                        .cornerRadius(8)
                @unknown default:
                    EmptyView()
                }
            }
            
            Text(String(format: "%.1fs", frame.timestamp))
                .font(.caption2)
                .foregroundColor(.secondary)
        }
    }
}

// MARK: - 基础帧详情视图
struct BaseFrameDetailView: View {
    let frame: BaseFrameData
    @Binding var isZoomed: Bool
    @Environment(\.dismiss) private var dismiss
    
    var body: some View {
        NavigationStack {
            VStack {
                AsyncImage(url: frame.thumbnailURL) { phase in
                    switch phase {
                    case .empty:
                        ProgressView()
                            .frame(maxWidth: .infinity, maxHeight: .infinity)
                    case .success(let image):
                        image
                            .resizable()
                            .aspectRatio(contentMode: isZoomed ? .fit : .fill)
                            .frame(maxWidth: .infinity, maxHeight: .infinity)
                            .clipped()
                            .scaleEffect(isZoomed ? 1.2 : 1.0)
                            .animation(.easeInOut(duration: 0.3), value: isZoomed)
                    case .failure:
                        Image(systemName: "photo")
                            .font(.largeTitle)
                            .foregroundColor(.secondary)
                            .frame(maxWidth: .infinity, maxHeight: .infinity)
                            .background(Color(.systemGray5))
                    @unknown default:
                        EmptyView()
                    }
                }
            }
            .navigationTitle("第 \(frame.frameIndex + 1) 帧")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button(action: {
                        isZoomed.toggle()
                    }) {
                        Image(systemName: isZoomed ? "arrow.down.left.and.arrow.up.right" : "arrow.up.left.and.arrow.down.right")
                    }
                }
                
                ToolbarItem(placement: .navigationBarLeading) {
                    Button("关闭") {
                        dismiss()
                    }
                }
            }
        }
    }
}

// MARK: - 基础帧提取状态视图
struct BaseFrameExtractionStatusView: View {
    @ObservedObject var viewModel: BaseFrameExtractionViewModel
    
    var body: some View {
        VStack(spacing: 16) {
            // 状态图标
            statusIcon
            
            // 状态文本
            Text(viewModel.statusDescription)
                .font(.headline)
                .multilineTextAlignment(.center)
            
            // 进度条
            if viewModel.isLoading {
                ProgressView(value: viewModel.progress)
                    .progressViewStyle(LinearProgressViewStyle())
                    .frame(maxWidth: 200)
            }
            
            // 错误信息
            if let errorMessage = viewModel.errorMessage {
                Text(errorMessage)
                    .font(.caption)
                    .foregroundColor(.red)
                    .multilineTextAlignment(.center)
            }
            
            // 重试按钮
            if case .failed = viewModel.status {
                Button(action: {
                    // 重试逻辑由父视图处理
                }) {
                    Label("重试", systemImage: "arrow.clockwise")
                        .font(.body)
                }
                .buttonStyle(.bordered)
            }
        }
        .padding()
    }
    
    private var statusIcon: some View {
        Group {
            switch viewModel.status {
            case .idle:
                Image(systemName: "photo")
                    .font(.largeTitle)
                    .foregroundColor(.secondary)
            case .extracting:
                ProgressView()
                    .scaleEffect(1.5)
            case .completed:
                Image(systemName: "checkmark.circle.fill")
                    .font(.largeTitle)
                    .foregroundColor(.green)
            case .failed:
                Image(systemName: "exclamationmark.triangle.fill")
                    .font(.largeTitle)
                    .foregroundColor(.red)
            }
        }
    }
}

#Preview {
    let mockFrames = [
        BaseFrameData(framePath: "https://example.com/frame1.jpg", frameIndex: 0, timestamp: 0.0),
        BaseFrameData(framePath: "https://example.com/frame2.jpg", frameIndex: 1, timestamp: 1.0),
        BaseFrameData(framePath: "https://example.com/frame3.jpg", frameIndex: 2, timestamp: 2.0)
    ]
    
    return VStack(spacing: 20) {
        BaseFramePreviewView(baseFrames: mockFrames)
            .frame(height: 200)
        
        BaseFramePreviewView(baseFrames: [])
            .frame(height: 200)
    }
    .padding()
}