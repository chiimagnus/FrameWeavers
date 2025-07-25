import SwiftUI

/// 处理加载视图组件
struct ProcessingLoadingView: View {
    let progress: Double
    let status: UploadStatus
    
    var body: some View {
        VStack(spacing: 15) {
            Text(statusText)
                .font(.system(size: 16))
                .foregroundColor(.gray)
            
            ZStack(alignment: .leading) {
                Capsule().fill(Color.black.opacity(0.1))
                Capsule()
                    .fill(Color.gray.opacity(0.8))
                    .frame(width: 200 * CGFloat(progress))
            }
            .frame(width: 200, height: 6)
            
            Text("\(Int(progress * 100))%")
                .font(.system(size: 14))
                .foregroundColor(.gray)
        }
    }
    
    /// 根据状态获取对应的文本
    private var statusText: String {
        switch status {
        case .pending: return "准备中..."
        case .uploading: return "上传中..."
        case .processing: return "正在生成你的回忆画册..."
        case .completed: return "处理完成！"
        case .failed: return "处理失败"
        }
    }
}