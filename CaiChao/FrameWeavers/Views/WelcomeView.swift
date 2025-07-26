import SwiftUI
import PhotosUI

struct WelcomeView: View {
    @Binding var selectedItems: [PhotosPickerItem]
    @State private var showingSampleAlbums = false

    var body: some View {
        VStack(spacing: 40) {
            Image("icon-home")
                .resizable()
                .frame(width: 100, height: 100)
                .shadow(radius: 10)

            TypewriterView(
                text: """
                有些故事，
                是你想和亲人分享的美好瞬间，
                可是视频给我们的时间太短，
                不足以停留在此刻。

                我们想说，我们想分享，
                此时此刻的故事。

                或许我们还想体验，
                和你的故事一致的风格，
                或许我们需要一个氛围，
                让你讲出属于你自己的故事。
                """,
                typeSpeed: 0.08
            )
            .font(.custom("STKaiti", size: 18))
            .multilineTextAlignment(.center)
            .foregroundColor(Color(hex: "#2F2617"))
            .lineSpacing(10)

            PhotosPicker(
                selection: $selectedItems,
                maxSelectionCount: 5,  // 最多选择5个视频
                matching: .videos,
                photoLibrary: .shared()
            ) {
                ZStack {
                    Image("button-import")
                        .resizable()
                        .aspectRatio(contentMode: .fit)
                        .frame(width: 250, height: 44)
                    
                    Text("开启一段故事织造")
                        .font(.custom("WSQuanXing", size: 24))
                        .foregroundColor(Color(hex: "#855C23"))
                }
            }
            
            Button(action: {
                showingSampleAlbums = true
            }) {
                Text("示例画册")
                    .font(.custom("STKaiti", size: 16))
                    .foregroundColor(Color(hex: "#855C23"))
                    .padding(.horizontal, 20)
                    // .padding(.vertical, 10)
                    .background(
                        RoundedRectangle(cornerRadius: 20)
                            .stroke(Color(hex: "#855C23"), lineWidth: 1)
                    )
            }

            Text("""
            最多上传5段3分钟内的视频
            选择有故事的片段效果更佳
            """)
                .font(.custom("STKaiti", size: 12))
                .fontWeight(.bold)
                .multilineTextAlignment(.center)
                .foregroundColor(Color(hex: "#2F2617"))
                .tracking(1.2)
                .lineSpacing(10)
        }
        .padding()
        .navigationBarTitleDisplayMode(.inline)
        .fullScreenCover(isPresented: $showingSampleAlbums) {
            SampleAlbumsView()
        }
    }
}