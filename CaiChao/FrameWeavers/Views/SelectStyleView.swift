import SwiftUI

struct SelectStyleView: View {
    @Environment(\.dismiss) private var dismiss
    
    var body: some View {
        ZStack {
            Image("背景单色")
                .resizable()
                .scaledToFill()

            VStack(spacing: 30) {
                Text("· 选择故事风格 ·")
                    .font(.custom("Kaiti SC", size: 16))
                    .fontWeight(.bold)
                    .foregroundColor(Color(hex: "#2F2617"))
                
                ZStack {
                    Image("四象限")
                        .resizable()
                        .scaledToFill()
                        .frame(width: 400, height: 400)
                    
                    // 图钉图标 - 右上角
                    Image("图钉")
                        .resizable()
                        .scaledToFit()
                        .frame(width: 60, height: 60)
                        .position(x: 370, y: 30)
                    
                    // 第一象限 - 文艺哲学 (左上)
                    Text("""
                        文艺
                        哲学
                        """)
                        .font(.custom("Kaiti SC", size: 24))
                        .fontWeight(.bold)
                        .foregroundColor(Color(hex: "#855C23"))
                        .position(x: 100, y: 100)
                    
                    // 第二象限 - 童话想象 (右上)
                    Text("""
                        童话
                        想象
                        """)
                        .font(.custom("Kaiti SC", size: 24))
                        .fontWeight(.bold)
                        .foregroundColor(Color(hex: "#855C23"))
                        .position(x: 300, y: 100)
                    
                    // 第三象限 - 悬念反转 (左下)
                    Text("""
                        悬念
                        反转
                        """)
                        .font(.custom("Kaiti SC", size: 24))
                        .fontWeight(.bold)
                        .foregroundColor(Color(hex: "#855C23"))
                        .position(x: 100, y: 300)
                    
                    // 第四象限 - 生活散文 (右下)
                    Text("""
                        生活
                        散文
                        """)
                        .font(.custom("Kaiti SC", size: 24))
                        .fontWeight(.bold)
                        .foregroundColor(Color(hex: "#855C23"))
                        .position(x: 300, y: 300)
                }
                .frame(width: 400, height: 400)
                .padding(.horizontal)

                ZStack{
                    Image("翻开画册")
                        .resizable()
                        .aspectRatio(contentMode: .fit)
                        .frame(width: 250, height: 44)

                    Text("开始生成")
                        .font(.custom("Kaiti SC", size: 24))
                        .fontWeight(.bold)
                        .foregroundColor(Color(hex: "#855C23"))

                }
            }
        }
        .ignoresSafeArea()
    }
}

// MARK: - SwiftUI Preview
struct SelectStyleView_Previews: PreviewProvider {
    static var previews: some View {
        SelectStyleView()
    }
}
