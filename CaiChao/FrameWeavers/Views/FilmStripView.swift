import SwiftUI

struct FilmStripView: View {
    @State private var offset: CGFloat = 0
    @State private var selectedIndex: Int? = nil
    
    private let imageCount = 6
    private let size: CGFloat = 60
    private let spacing: CGFloat = 16
    
    var body: some View {
        VStack(spacing: 40) {
            // 主显示区域
            if let index = selectedIndex {
                Image(systemName: "photo")
                    .font(.system(size: 120))
                    .foregroundColor(.blue)
                    .transition(.scale)
            } else {
                Text("点击胶片选择")
                    .foregroundColor(.gray)
            }
            
            // 胶片滚动区域
            GeometryReader { geo in
                ScrollView(.horizontal, showsIndicators: false) {
                    HStack(spacing: spacing) {
                        ForEach(0..<imageCount * 3, id: \.self) { i in
                            let idx = i % imageCount
                            Button {
                                withAnimation(.spring()) {
                                    selectedIndex = idx
                                }
                            } label: {
                                Image(systemName: "photo")
                                    .font(.system(size: size))
                                    .foregroundColor(.white)
                                    .padding()
                                    .background(Color.gray.opacity(0.3))
                                    .cornerRadius(8)
                            }
                        }
                    }
                    .padding(.horizontal)
                    .offset(x: offset)
                }
                .disabled(true)
                .onAppear { startAnimation() }
            }
            .frame(height: 100)
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .background(Color.black)
    }
    
    private func startAnimation() {
        let width = CGFloat(imageCount) * (size + spacing)
        withAnimation(.linear(duration: 10).repeatForever(autoreverses: false)) {
            offset = -width
        }
    }
}

#Preview {
    FilmStripView()
}