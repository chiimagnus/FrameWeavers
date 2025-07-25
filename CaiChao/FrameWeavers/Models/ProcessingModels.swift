import SwiftUI

// MARK: - Data Models and PreferenceKeys

/// 用于在视图树中向上传递视图的Frame信息
struct FramePreferenceKey: PreferenceKey {
    static var defaultValue: [String: CGRect] = [:]
    
    static func reduce(value: inout [String : CGRect], nextValue: () -> [String : CGRect]) {
        value.merge(nextValue(), uniquingKeysWith: { $1 })
    }
}

/// 飞行图片的信息
struct FlyingImageInfo: Identifiable {
    let id: String
    let sourceFrame: CGRect
}