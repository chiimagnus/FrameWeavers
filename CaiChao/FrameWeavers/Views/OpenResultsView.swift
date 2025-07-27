import SwiftUI
import PhotosUI

struct OpenResultsView: View {
    @Environment(\.dismiss) private var dismiss
    let comicResult: ComicResult
    
    var body: some View {
        ZStack {
            Image("背景单色")
                .resizable()
                .scaledToFill()
                .ignoresSafeArea()
            
            VStack(spacing: 40) {
                // 显示第一页的图片作为封面
                if let firstPanel = comicResult.panels.first {
                    AsyncImageView(imageUrl: firstPanel.imageUrl)
                        .aspectRatio(contentMode: .fit)
                        .frame(maxHeight: 300)
                        .shadow(radius: 10)
                        .padding(.horizontal, 20)
                } else {
                    // 如果没有页面，显示默认封面
                    Image("封面")
                        .resizable()
                        .scaledToFit()
                        .frame(maxHeight: 300)
                        .shadow(radius: 10)
                        .padding(.horizontal, 20)
                }

                VStack(spacing: 16) {
                    // 显示连环画标题
                    Text(comicResult.title)
                        .font(.custom("WSQuanXing", size: 24))
                        .fontWeight(.bold)
                        .foregroundColor(Color(hex: "#855C23"))
                        .multilineTextAlignment(.center)
                        .padding(.horizontal, 20)

                    // 显示第一页的旁白作为描述
                    if let firstPanel = comicResult.panels.first, let narration = firstPanel.narration {
                        Text(narration)
                            .font(.custom("STKaiti", size: 16))
                            .fontWeight(.bold)
                            .foregroundColor(Color(red: 0.18, green: 0.15, blue: 0.09))
                            .opacity(0.6)
                            .multilineTextAlignment(.center)
                            .padding(.horizontal, 20)
                            .lineLimit(4)
                    }
                }

                
                NavigationLink {
                    ComicResultView(comicResult: comicResult)
                } label: {
                    ZStack {
                        Image("翻开画册")
                            .resizable()
                            .aspectRatio(contentMode: .fit)
                            .frame(width: 250, height: 44)
                        
                        Text("翻开画册")
                            .font(.custom("WSQuanXing", size: 24))
                            .fontWeight(.bold)
                            .foregroundColor(Color(hex: "#855C23"))
                    }
                }
            }
            .padding()
            .navigationBarBackButtonHidden(true)
        }
    }
}
