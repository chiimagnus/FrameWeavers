import SwiftUI

struct ComicResultView: View {
    let comicResult: ComicResult
    
    var body: some View {
        ScrollView {
            VStack(spacing: 20) {
                Text("连环画生成完成！")
                    .font(.title2.bold())
                
                ForEach(comicResult.panels) { panel in
                    VStack(alignment: .leading, spacing: 8) {
                        AsyncImage(url: URL(string: panel.imageUrl)) { image in
                            image
                                .resizable()
                                .aspectRatio(contentMode: .fit)
                        } placeholder: {
                            ProgressView()
                                .frame(height: 200)
                        }
                        .frame(maxWidth: .infinity)
                        .background(Color.gray.opacity(0.1))
                        .cornerRadius(8)
                        
                        if let narration = panel.narration {
                            Text(narration)
                                .font(.body)
                                .padding(.horizontal)
                        }
                    }
                }
                
                VStack(alignment: .leading, spacing: 12) {
                    Text("互动问题")
                        .font(.headline)
                    
                    ForEach(comicResult.finalQuestions, id: \.self) { question in
                        Text("• \(question)")
                            .font(.body)
                    }
                }
                .padding()
            }
            .padding()
        }
        .navigationTitle("连环画结果")
    }
}
