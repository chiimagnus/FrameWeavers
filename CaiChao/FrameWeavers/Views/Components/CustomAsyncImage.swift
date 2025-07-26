import SwiftUI
import Foundation

/// 自定义AsyncImage，支持自定义HTTP头
struct CustomAsyncImage<Content: View, Placeholder: View>: View {
    let url: URL?
    let content: (Image) -> Content
    let placeholder: () -> Placeholder
    
    @State private var image: UIImage?
    @State private var isLoading = false
    @State private var error: Error?
    
    init(
        url: URL?,
        @ViewBuilder content: @escaping (Image) -> Content,
        @ViewBuilder placeholder: @escaping () -> Placeholder
    ) {
        self.url = url
        self.content = content
        self.placeholder = placeholder
    }
    
    var body: some View {
        Group {
            if let image = image {
                content(Image(uiImage: image))
            } else if isLoading {
                placeholder()
            } else if error != nil {
                Rectangle()
                    .fill(Color.red.opacity(0.3))
                    .overlay(
                        VStack {
                            Text("加载失败")
                                .font(.caption)
                                .foregroundColor(.white)
                            if let error = error {
                                Text(error.localizedDescription)
                                    .font(.caption2)
                                    .foregroundColor(.white.opacity(0.7))
                            }
                        }
                    )
            } else {
                placeholder()
            }
        }
        .onAppear {
            loadImage()
        }
        .onChange(of: url) { _, _ in
            loadImage()
        }
    }
    
    private func loadImage() {
        guard let url = url else { return }
        
        isLoading = true
        error = nil
        image = nil
        
        Task {
            do {
                // 创建带有正确头部的请求
                var request = URLRequest(url: url)
                request.setValue("Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1", forHTTPHeaderField: "User-Agent")
                request.setValue("image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8", forHTTPHeaderField: "Accept")
                request.setValue("gzip, deflate, br", forHTTPHeaderField: "Accept-Encoding")
                request.setValue("keep-alive", forHTTPHeaderField: "Connection")
                request.setValue("same-origin", forHTTPHeaderField: "Sec-Fetch-Site")
                request.setValue("no-cors", forHTTPHeaderField: "Sec-Fetch-Mode")
                request.setValue("image", forHTTPHeaderField: "Sec-Fetch-Dest")
                
                print("🖼️ CustomAsyncImage: 开始加载图片: \(url.absoluteString)")
                
                let (data, response) = try await URLSession.shared.data(for: request)
                
                if let httpResponse = response as? HTTPURLResponse {
                    print("🖼️ CustomAsyncImage: HTTP状态码: \(httpResponse.statusCode)")
                    print("🖼️ CustomAsyncImage: Content-Type: \(httpResponse.value(forHTTPHeaderField: "Content-Type") ?? "未知")")
                    print("🖼️ CustomAsyncImage: Content-Length: \(httpResponse.value(forHTTPHeaderField: "Content-Length") ?? "未知")")

                    guard httpResponse.statusCode == 200 else {
                        throw URLError(.badServerResponse)
                    }

                    // 检查Content-Type是否为图片
                    if let contentType = httpResponse.value(forHTTPHeaderField: "Content-Type"),
                       !contentType.hasPrefix("image/") {
                        print("❌ CustomAsyncImage: 服务器返回的不是图片，而是: \(contentType)")
                        if let responseString = String(data: data, encoding: .utf8) {
                            print("📄 CustomAsyncImage: 响应内容前200字符: \(String(responseString.prefix(200)))")
                        }
                        throw URLError(.cannotDecodeContentData)
                    }
                }

                guard let uiImage = UIImage(data: data) else {
                    print("❌ CustomAsyncImage: 无法将数据解码为图片，数据大小: \(data.count) bytes")
                    if let responseString = String(data: data, encoding: .utf8) {
                        print("📄 CustomAsyncImage: 数据内容前200字符: \(String(responseString.prefix(200)))")
                    }
                    throw URLError(.cannotDecodeContentData)
                }
                
                await MainActor.run {
                    self.image = uiImage
                    self.isLoading = false
                    print("✅ CustomAsyncImage: 图片加载成功")
                }
                
            } catch {
                await MainActor.run {
                    self.error = error
                    self.isLoading = false
                    print("❌ CustomAsyncImage: 图片加载失败: \(error.localizedDescription)")
                }
            }
        }
    }
}

// 便利初始化器
extension CustomAsyncImage where Content == Image, Placeholder == ProgressView<EmptyView, EmptyView> {
    init(url: URL?) {
        self.init(
            url: url,
            content: { $0 },
            placeholder: { ProgressView() }
        )
    }
}
