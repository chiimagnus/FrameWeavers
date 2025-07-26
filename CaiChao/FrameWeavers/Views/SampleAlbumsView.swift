import SwiftUI

struct SampleAlbumsView: View {
    @Environment(\.dismiss) private var dismiss
    
    // 示例画册数据
    private let sampleAlbums: [SampleAlbum] = [
        SampleAlbum(
            id: "sample-001",
            title: "都市精灵的秘境",
            description: "少女爱丽丝与古老精灵的奇幻冒险",
            coverImage: "封面",
            comicResult: ComicResult(
                comicId: "sample-001",
                deviceId: "sample-device",
                originalVideoTitle: "都市精灵的秘境",
                creationDate: "2025-07-26",
                panelCount: 4,
                panels: [
                    ComicPanel(
                        panelNumber: 1,
                        imageUrl: "Image1",
                        narration: "在钢筋水泥的都市中，藏着一片不为人知的秘境。少女爱丽丝，一个能听懂风语花言的女孩，在一次午后小憩中，无意间听到了来自古老精灵的微弱呼唤。"
                    ),
                    ComicPanel(
                        panelNumber: 2,
                        imageUrl: "Image2",
                        narration: "精灵告诉她，这片秘境正在被都市的污染慢慢侵蚀，如果不及时拯救，这里的所有生灵都将消失。爱丽丝看着眼前这个只有巴掌大小的精灵，心中涌起了强烈的保护欲。"
                    ),
                    ComicPanel(
                        panelNumber: 3,
                        imageUrl: "Image3",
                        narration: "为了拯救被污染的自然，她必须与精灵签下契约。然而契约的代价，是她自己的生命力。每使用一次净化魔法，她的寿命就会减少一年。"
                    ),
                    ComicPanel(
                        panelNumber: 4,
                        imageUrl: "Image4",
                        narration: "爱丽丝毫不犹豫地签下了契约。她相信，用自己的生命换来这片秘境的重生，是值得的。因为有些美好，值得用生命去守护。"
                    )
                ],
                finalQuestions: [
                    "如果你是爱丽丝，你会选择签下这个契约吗？",
                    "你觉得什么样的事物值得用生命去守护？",
                    "在现实生活中，我们应该如何保护环境？"
                ]
            )
        ),
        SampleAlbum(
            id: "sample-002",
            title: "空白画册 #2",
            description: "即将到来的精彩故事",
            coverImage: "封面",
            comicResult: nil
        ),
        SampleAlbum(
            id: "sample-003",
            title: "空白画册 #3",
            description: "等待你的创作",
            coverImage: "封面",
            comicResult: nil
        )
    ]
    
    var body: some View {
        NavigationView {
            ZStack {
                Image("背景单色")
                    .resizable()
                    .scaledToFill()
                    .ignoresSafeArea()
                
                VStack(spacing: 20) {
                    Text("示例画册")
                        .font(.custom("WSQuanXing", size: 28))
                        .foregroundColor(Color(hex: "#855C23"))
                        .padding(.top, 20)
                    
                    Text("体验连环画的魅力")
                        .font(.custom("STKaiti", size: 16))
                        .foregroundColor(Color(hex: "#2F2617"))
                        .opacity(0.8)
                    
                    ScrollView {
                        LazyVStack(spacing: 16) {
                            ForEach(sampleAlbums) { album in
                                SampleAlbumRowView(album: album)
                            }
                        }
                        .padding(.horizontal, 20)
                    }
                }
            }
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarLeading) {
                    Button("关闭") {
                        dismiss()
                    }
                    .font(.custom("STKaiti", size: 16))
                    .foregroundColor(Color(hex: "#855C23"))
                }
            }
        }
    }
}

// 示例画册数据模型
struct SampleAlbum: Identifiable {
    let id: String
    let title: String
    let description: String
    let coverImage: String
    let comicResult: ComicResult?
}

// 单个画册行视图
struct SampleAlbumRowView: View {
    let album: SampleAlbum

    var body: some View {
        if let comicResult = album.comicResult {
            // 有内容的画册 - 可以点击
            NavigationLink {
                SampleFlowView(comicResult: comicResult)
            } label: {
                albumRowContent
            }
        } else {
            // 空白画册 - 不可点击
            albumRowContent
                .opacity(0.6)
        }
    }
    
    private var albumRowContent: some View {
        HStack(spacing: 16) {
            // 封面图片
            Image(album.coverImage)
                .resizable()
                .aspectRatio(contentMode: .fit)
                .frame(width: 80, height: 100)
                .cornerRadius(8)
                .shadow(radius: 4)
            
            // 文本信息
            VStack(alignment: .leading, spacing: 8) {
                Text(album.title)
                    .font(.custom("WSQuanXing", size: 20))
                    .foregroundColor(Color(hex: "#2F2617"))
                    .lineLimit(1)
                
                Text(album.description)
                    .font(.custom("STKaiti", size: 14))
                    .foregroundColor(Color(hex: "#2F2617"))
                    .opacity(0.7)
                    .lineLimit(2)
                
                if album.comicResult != nil {
                    HStack {
                        Image(systemName: "book.fill")
                            .font(.caption)
                            .foregroundColor(Color(hex: "#855C23"))
                        
                        Text("点击阅读")
                            .font(.custom("STKaiti", size: 12))
                            .foregroundColor(Color(hex: "#855C23"))
                    }
                } else {
                    HStack {
                        Image(systemName: "clock")
                            .font(.caption)
                            .foregroundColor(.gray)
                        
                        Text("敬请期待")
                            .font(.custom("STKaiti", size: 12))
                            .foregroundColor(.gray)
                    }
                }
            }
            
            Spacer()
            
            // 右侧箭头（仅对有内容的画册显示）
            if album.comicResult != nil {
                Image(systemName: "chevron.right")
                    .font(.caption)
                    .foregroundColor(Color(hex: "#855C23"))
            }
        }
        .padding(16)
        .background(Color.white.opacity(0.9))
        .cornerRadius(12)
        .shadow(radius: 2)
    }
}

#Preview {
    SampleAlbumsView()
}
