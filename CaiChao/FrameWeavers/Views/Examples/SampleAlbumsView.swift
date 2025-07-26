import SwiftUI

struct SampleAlbumsView: View {
    @Environment(\.dismiss) private var dismiss
    
    // 示例画册数据
    private let sampleAlbums: [SampleAlbum] = [
        SampleAlbum(
            id: "sample-001",
            title: "时光里的温暖记忆",
            description: "一个关于家庭温情的美好故事",
            coverImage: "封面",
            comicResult: ComicResult(
                comicId: "sample-001",
                deviceId: "sample-device",
                originalVideoTitle: "时光里的温暖记忆",
                creationDate: "2025-07-26",
                panelCount: 3,
                panels: [
                    ComicPanel(
                        panelNumber: 1,
                        imageUrl: "1-第1页",
                        narration: "阳光透过窗棂洒在桌案上，奶奶正在为即将远行的孙女准备行囊。每一件衣物都被细心地叠好，每一样物品都承载着满满的爱意。"
                    ),
                    ComicPanel(
                        panelNumber: 2,
                        imageUrl: "1-第2页",
                        narration: "小女孩依偎在奶奶身边，听着那些讲了无数遍却永远不厌倦的故事。奶奶温暖的怀抱，是这世界上最安全的港湾。"
                    ),
                    ComicPanel(
                        panelNumber: 3,
                        imageUrl: "1-第3页",
                        narration: "离别的时刻终于到来，奶奶将一个小小的香囊塞进孙女的手中。'无论走到哪里，都要记得回家的路。'奶奶的话语如春风般温柔。"
                    )
                ],
                finalQuestions: [
                    "你还记得和家人在一起的温暖时光吗？",
                    "什么样的物品能让你想起家的温暖？",
                    "长大后，你会如何回报家人的爱？"
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
