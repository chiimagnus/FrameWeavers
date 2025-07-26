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
            title: "小猫的冒险之旅",
            description: "一只勇敢小猫的奇妙探险",
            coverImage: "封面",
            comicResult: ComicResult(
                comicId: "sample-002",
                deviceId: "sample-device",
                originalVideoTitle: "小猫的冒险之旅",
                creationDate: "2025-07-26",
                panelCount: 4,
                panels: [
                    ComicPanel(
                        panelNumber: 1,
                        imageUrl: "2-第1页",
                        narration: "在一个宁静的小镇上，住着一只名叫小花的橘猫。她总是对窗外的世界充满好奇，梦想着有一天能够走出家门，去探索那个未知的大世界。"
                    ),
                    ComicPanel(
                        panelNumber: 2,
                        imageUrl: "2-第2页",
                        narration: "终于有一天，主人忘记关门了。小花悄悄溜了出去，踏上了她的第一次冒险。街道上的一切都是那么新奇，每一个角落都藏着惊喜。"
                    ),
                    ComicPanel(
                        panelNumber: 3,
                        imageUrl: "2-第3页",
                        narration: "在公园里，小花遇到了一群友善的流浪猫。他们教会了她如何在野外生存，如何寻找食物，如何躲避危险。小花学会了很多从未想过的技能。"
                    ),
                    ComicPanel(
                        panelNumber: 4,
                        imageUrl: "2-第4页",
                        narration: "当夜幕降临时，小花想起了温暖的家。她带着满满的回忆和新朋友们的祝福，踏上了回家的路。从此，她既珍惜家的温暖，也不忘记外面世界的精彩。"
                    )
                ],
                finalQuestions: [
                    "你觉得小花最大的收获是什么？",
                    "如果你是小花，你会选择留在外面还是回家？",
                    "这个故事告诉我们关于勇气和成长的什么道理？"
                ]
            )
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
