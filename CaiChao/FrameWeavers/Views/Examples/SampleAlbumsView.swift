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
                title: "时光里的温暖记忆",  // 添加故事标题
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
                title: "小猫的冒险之旅",  // 添加故事标题
                originalVideoTitle: "小猫的冒险之旅",
                creationDate: "2025-07-26",
                panelCount: 4,
                panels: [
                    ComicPanel(
                        panelNumber: 1,
                        imageUrl: "2-第1页",
                        narration: "有些旅程，从一张牌、一个无关紧要的输赢开始。窗外的世界向后飞驰，而前方的未知，在笑声中悄然展开。"
                    ),
                    ComicPanel(
                        panelNumber: 2,
                        imageUrl: "2-第2页",
                        narration: "她曾以为，旅途的意义在于抵达。直到她捧着那束向日葵，在陌生的绿意前停下脚步，才发现，有些风景，是为了让你与自己重逢。"
                    ),
                    ComicPanel(
                        panelNumber: 3,
                        imageUrl: "2-第3页",
                        narration: "而那些不期而遇的浪漫，就像街角突然出现的玫瑰，提醒着她，这世界总有人在笨拙而热烈地爱着你。"
                    ),
                    ComicPanel(
                        panelNumber: 4,
                        imageUrl: "2-第4页",
                        narration: "记忆里最滚烫的，往往是街头巷尾的烟火气。一串烤红薯的香甜，和朋友分享的蓝色围巾，共同织就了那个回不去的午后。"
                    ),
                    ComicPanel(
                        panelNumber: 5,
                        imageUrl: "2-第5页",
                        narration: "他们曾一起走向那座名为“大理”的城，走向历史的深处。每个人都以为是在奔赴一场盛大的风景，其实，不过是奔赴一场早已注定的相遇。"
                    ),
                    ComicPanel(
                        panelNumber: 6,
                        imageUrl: "2-第6页",
                        narration: "在沉睡的文物之间，她试图寻找时间的答案。每一个凝视，都是一场跨越千年的对话。"
                    ),
                    ComicPanel(
                        panelNumber: 7,
                        imageUrl: "2-第7页",
                        narration: "现代的我和古老的谜，在这趟旅途中反复交织。一面是率性的牛仔，一面是肃穆的东方，共同拼凑出完整的灵魂。"
                    ),
                    ComicPanel(
                        panelNumber: 8,
                        imageUrl: "2-第8页",
                        narration: "后来，所有的风景与奇遇，都定格在了一张用力的自拍里。笑容是真的，友谊是真的，那个在市集里喧闹的黄昏，也是真的。"
                    ),
                    ComicPanel(
                        panelNumber: 9,
                        imageUrl: "2-第9页",
                        narration: "人们在网红打卡点寻找诗和远方，而他在路边，用一束鲜花，等待着他的全世界。"
                    ),
                    ComicPanel(
                        panelNumber: 10,
                        imageUrl: "2-第10页",
                        narration: "旅途的最后，是一场告别的雪。快门留住了青春的温度，却留不住那终将融化的时光。"
                    ),
                    ComicPanel(
                        panelNumber: 11,
                        imageUrl: "2-第11页",
                        narration: "直到凌晨两点五十五分，手机屏幕里的吉光片羽才泄露了秘密——所有鲜活的过往，都已成为睡前的浏览记录。"
                    ),
                    ComicPanel(
                        panelNumber: 12,
                        imageUrl: "2-第12页",
                        narration: "指尖最终停在了查询页面。目的地四川，时间十月三日，状态却是“暂无车辆信息”。原来，这场盛大的回忆，只是一场无法启程的计划。"
                    )
                ],
                finalQuestions: [
                    "如果让你从这段旅程中选一个瞬间定格成永恒，你会选择哪个画面？",
                    "这些故事里藏着许多“笨拙而热烈”的爱——街角玫瑰、路边鲜花、蓝色围巾...你生命中有过这样被悄悄爱着的时刻吗？",
                    "最后那条“无法启程的四川之旅”像不像我们人生中某些注定错过的美好？"
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
