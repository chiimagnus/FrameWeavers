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
            }
        }
        .ignoresSafeArea()
    }
}
