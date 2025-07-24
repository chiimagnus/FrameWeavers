import SwiftUI

struct ComicResultView: View {
    let comicResult: ComicResult
    @State private var currentPage = 0
    
    var body: some View {
        GeometryReader { geometry in
            VStack(spacing: 0) {
                // 页面指示器
                HStack {
                    Spacer()
                    Text("\(currentPage + 1)/\(comicResult.panels.count)")
                        .font(.headline)
                        .foregroundColor(.white)
                        .padding(.horizontal, 16)
                        .padding(.vertical, 8)
                        .background(Color.black.opacity(0.7))
                        .cornerRadius(20)
                        .padding(.top, 8)
                    Spacer()
                }
                
                // 分页内容
                TabView(selection: $currentPage) {
                    ForEach(0..<comicResult.panels.count, id: \.self) { index in
                        let panel = comicResult.panels[index]
                        VStack(spacing: 20) {
                            AsyncImage(url: URL(string: panel.imageUrl)) { image in
                                image
                                    .resizable()
                                    .aspectRatio(contentMode: .fit)
                            } placeholder: {
                                ProgressView()
                                    .frame(height: geometry.size.height * 0.6)
                            }
                            .frame(maxWidth: .infinity, maxHeight: geometry.size.height * 0.7)
                            .background(Color.gray.opacity(0.1))
                            .cornerRadius(8)
                            
                            if let narration = panel.narration {
                                Text(narration)
                                    .font(.body)
                                    .padding(.horizontal)
                                    .frame(maxWidth: .infinity, alignment: .leading)
                            }
                        }
                        .tag(index)
                    }
                }
                .tabViewStyle(PageTabViewStyle(indexDisplayMode: .never))
                .indexViewStyle(PageIndexViewStyle(backgroundDisplayMode: .never))
                
                // 互动问题区域
                if currentPage == comicResult.panels.count - 1 {
                    VStack(alignment: .leading, spacing: 12) {
                        Text("互动问题")
                            .font(.headline)
                        
                        ForEach(comicResult.finalQuestions, id: \.self) { question in
                            Text("• \(question)")
                                .font(.body)
                        }
                    }
                    .padding()
                    .frame(maxWidth: .infinity)
                    .background(Color(UIColor.systemBackground))
                }
            }
        }
        .navigationTitle("连环画结果")
        .navigationBarTitleDisplayMode(.inline)
        .onAppear {
            // 强制横屏
            if #available(iOS 16.0, *) {
                let windowScene = UIApplication.shared.connectedScenes.first as? UIWindowScene
                windowScene?.requestGeometryUpdate(.iOS(interfaceOrientations: .landscape))
            } else {
                // Fallback for earlier versions
                UIDevice.current.setValue(UIInterfaceOrientation.landscapeRight.rawValue, forKey: "orientation")
                UINavigationController.attemptRotationToDeviceOrientation()
            }
        }
        .onDisappear {
            // 恢复竖屏
            if #available(iOS 16.0, *) {
                let windowScene = UIApplication.shared.connectedScenes.first as? UIWindowScene
                windowScene?.requestGeometryUpdate(.iOS(interfaceOrientations: .portrait))
            } else {
                // Fallback for earlier versions
                UIDevice.current.setValue(UIInterfaceOrientation.portrait.rawValue, forKey: "orientation")
                UINavigationController.attemptRotationToDeviceOrientation()
            }
        }
    }
}
