import SwiftUI
import Combine

/// 处理画廊的视图模型
class ProcessingGalleryViewModel: ObservableObject {
    @Published var mainImageName: String = "Image1"
    @Published var flyingImageInfo: FlyingImageInfo?
    @Published var hideSourceImageId: String?
    // 移除currentScrollIndex，现在使用持续滚动
    @Published var stackedImages: [String] = [] // 已堆叠的图片列表

    let imageNames = ["Image1", "Image2", "Image3", "Image4", "Image1", "Image2", "Image3", "Image4"]
    
    var loopedImageNames: [String] {
        imageNames + imageNames + imageNames
    }
    
    init() {
        mainImageName = imageNames.first ?? ""
    }
    
    /// 触发一次图片跳跃动画（旧版本，保留兼容性）
    func triggerJumpAnimation(from frames: [String: CGRect]) {
        guard let centerImageId = findCenterImageId(from: frames),
              frames["photoStackTarget"] != nil else { return }

        // 如果图片已经在堆叠中，跳过
        if centerImageId == mainImageName || stackedImages.contains(centerImageId) { return }

        guard let sourceFrame = frames[centerImageId] else { return }

        triggerJumpAnimation(imageName: centerImageId, sourceFrame: sourceFrame)
    }

    /// 新的图片跳跃动画方法
    func triggerJumpAnimation(imageName: String, sourceFrame: CGRect) {
        // 如果图片已经在堆叠中或是当前主图片，跳过
        if imageName == mainImageName || stackedImages.contains(imageName) { return }

        self.flyingImageInfo = FlyingImageInfo(id: imageName, sourceFrame: sourceFrame)
        self.hideSourceImageId = imageName

        DispatchQueue.main.asyncAfter(deadline: .now() + 1.2) {
            // 将当前主图片添加到堆叠中（如果不为空且不在堆叠中）
            if !self.mainImageName.isEmpty && !self.stackedImages.contains(self.mainImageName) {
                self.stackedImages.append(self.mainImageName)
            }

            // 设置新的主图片
            self.mainImageName = imageName
            self.flyingImageInfo = nil
            self.hideSourceImageId = nil
        }
    }
    
    /// 根据Frame信息计算当前在中心的图片ID
    private func findCenterImageId(from frames: [String: CGRect]) -> String? {
        let screenCenter = UIScreen.main.bounds.midX
        var closestImageId: String?
        var minDistance = CGFloat.infinity

        // 过滤出有效的图片frame，并找到最接近屏幕中心的
        for (id, frame) in frames {
            // 确保frame不为零且图片名在列表中
            guard imageNames.contains(id), frame != .zero else { continue }

            let distance = abs(frame.midX - screenCenter)
            if distance < minDistance {
                minDistance = distance
                closestImageId = id
            }
        }
        return closestImageId
    }
}

// MARK: - VideoUploadViewModel Extension

extension VideoUploadViewModel {
    /// 使用项目中现有的图片资源
    var mockImageNames: [String] {
        return ["Image1", "Image2", "Image3", "Image4", "Image1", "Image2", "Image3", "Image4"]
    }
    
    /// 为了无缝滚动，复制数组
    var loopedImageNames: [String] {
        let images = mockImageNames
        return images + images + images
    }
}