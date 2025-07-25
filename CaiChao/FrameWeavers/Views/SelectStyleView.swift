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
                
                Image("四象限")
                    .resizable()
                    .scaledToFill()
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
