import SwiftUI

struct SelectStyleView: View {
    @Environment(\.dismiss) private var dismiss
    
    var body: some View {
        ZStack {
            Image("背景单色")
                .resizable()
                .scaledToFill()

            VStack(spacing: 30) {
                Text("选择风格")
                    .font(.custom("Kaiti SC", size: 28))
                    .fontWeight(.bold)
                    .foregroundColor(Color(hex: "#2F2617"))
                
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
