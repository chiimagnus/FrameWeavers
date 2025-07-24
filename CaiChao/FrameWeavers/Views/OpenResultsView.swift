import SwiftUI
import PhotosUI

struct OpenResultsView: View {
    let comicResult: ComicResult
    
    var body: some View {
        VStack(spacing: 40) {
            Image("封面")
                .resizable()
                .scaledToFit()
                // .frame(width: 100, height: 100)
                .shadow(radius: 10)
                .padding(.horizontal, 20)

            Text("在钢筋水泥的都市中，藏着一片不为人知的秘境。少女爱丽丝，一个能听懂风语花言的女孩，在一次午后小憩中，无意间听到了来自古老精灵的微弱呼唤。为了拯救被污染的自然，她必须与精灵签下契约，然而契约的代价，是她自己的生命力……")
                .font(.custom("Kaiti SC", size: 16))
                .fontWeight(.bold)
                .foregroundColor(Color(red: 0.18, green: 0.15, blue: 0.09))
                .frame(width: 275, height: 202.99998, alignment: .topLeading)
                .opacity(0.6)
            
            NavigationLink {
                ComicResultView(comicResult: comicResult)
            } label: {
                ZStack {
                    Image("翻开画册")
                        .resizable()
                        .aspectRatio(contentMode: .fit)
                        .frame(width: 250, height: 44)
                    
                    Text("翻开画册")
                        .font(.custom("Kaiti SC", size: 24))
                        .fontWeight(.bold)
                        .foregroundColor(Color(hex: "#855C23"))
                }
            }
        }
        .padding()
    }
}
