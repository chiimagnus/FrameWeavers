import SwiftUI

struct ComicResultView: View {
    let comicResult: ComicResult
    @State private var currentPage = 0
    @Environment(\.dismiss) private var dismiss
    @State private var dragOffset: CGFloat = 0
    @State private var isDragging = false
    
    var body: some View {
        GeometryReader { geometry in
            ZStack {
                Color(.systemBackground)
                    .edgesIgnoringSafeArea(.all)
                
                VStack(spacing: 0) {
                    // 顶部拖拽指示器
                    VStack {
                        Capsule()
                            .fill(Color.secondary.opacity(0.5))
                            .frame(width: 40, height: 4)
                            .padding(.top, 8)
                        
                        Spacer()
                    }
                    .frame(height: 30)
                    .opacity(isDragging ? 1.0 : 0.3)
                    
                    // 页面指示器 - 保持在顶部
                    HStack {
                        Spacer()
                        Text("\(currentPage + 1)/\(comicResult.panels.count)")
                            .font(.headline)
                            .foregroundColor(Color(.label))
                            .padding(.horizontal, 16)
                            .padding(.vertical, 8)
                            .background(Color(.systemBackground).opacity(0.7))
                            .cornerRadius(20)
                            .padding(.top, 8)
                        Spacer()
                    }
                    .padding(.top, geometry.safeAreaInsets.top)
                    
                    // 分页内容 - 横向布局
                    TabView(selection: $currentPage) {
                        ForEach(0..<comicResult.panels.count, id: \.self) { index in
                            let panel = comicResult.panels[index]
                            ComicPanelView(panel: panel, geometry: geometry)
                                .tag(index)
                        }
                    }
                    .tabViewStyle(PageTabViewStyle(indexDisplayMode: .never))
                    .indexViewStyle(PageIndexViewStyle(backgroundDisplayMode: .never))
                    
                    // 互动问题区域 - 仅在最后一页显示
                    if currentPage == comicResult.panels.count - 1 {
                        VStack(alignment: .leading, spacing: 12) {
                            Text("互动问题")
                                .font(.headline)
                                .foregroundColor(Color(.label))
                            
                            ForEach(comicResult.finalQuestions, id: \.self) { question in
                                Text("• \(question)")
                                    .font(.body)
                                    .foregroundColor(Color(.secondaryLabel))
                                    .lineSpacing(6)
                            }
                        }
                        .padding()
                        .frame(maxWidth: .infinity)
                        .background(Color(.systemBackground).opacity(0.3))
                        .cornerRadius(12)
                        .padding(.bottom, geometry.safeAreaInsets.bottom + 10)
                    }
                }
            }
            .offset(y: max(0, dragOffset))
            .animation(.spring(response: 0.3, dampingFraction: 0.8), value: dragOffset)
            .gesture(
                DragGesture()
                    .onChanged { value in
                        // 只允许从顶部向下滑动
                        if value.startLocation.y < 100 {
                            isDragging = true
                            dragOffset = max(0, value.translation.height)
                        }
                    }
                    .onEnded { value in
                        isDragging = false
                        if dragOffset > 100 {
                            // 滑动距离超过100点，关闭视图
                            dismiss()
                        } else {
                            // 滑动距离不足，恢复原位
                            dragOffset = 0
                        }
                    }
            )
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

// 单独的漫画页面视图组件
struct ComicPanelView: View {
    let panel: ComicPanel
    let geometry: GeometryProxy
    
    var body: some View {
        HStack(spacing: 20) {
            // 左侧图片区域 - 占据约60%宽度
            AsyncImage(url: URL(string: panel.imageUrl)) { phase in
                switch phase {
                case .success(let image):
                    image
                        .resizable()
                        .aspectRatio(contentMode: .fit)
                        .frame(
                            width: geometry.size.width * 0.6,
                            height: geometry.size.height * 0.75
                        )
                        .background(Color(.systemGray5))
                        .cornerRadius(12)
                        .clipped()
                    
                case .failure(_):
                    VStack {
                        Image(systemName: "photo")
                            .font(.largeTitle)
                            .foregroundColor(Color(.systemGray))
                        Text("图片加载失败")
                            .foregroundColor(Color(.systemGray))
                    }
                    .frame(
                        width: geometry.size.width * 0.6,
                        height: geometry.size.height * 0.75
                    )
                    .background(Color(.systemGray5))
                    .cornerRadius(12)
                    
                case .empty:
                    ProgressView()
                        .frame(
                            width: geometry.size.width * 0.6,
                            height: geometry.size.height * 0.75
                        )
                        .background(Color(.systemGray5))
                        .cornerRadius(12)
                @unknown default:
                    EmptyView()
                }
            }
            
            // 右侧文本区域 - 占据约35%宽度
            if let narration = panel.narration {
                ScrollView {
                    VStack(alignment: .leading, spacing: 16) {
                        Text("故事叙述")
                            .font(.title3.bold())
                            .foregroundColor(Color(.label))
                        
                        Text(narration)
                            .font(.body)
                            .foregroundColor(Color(.secondaryLabel))
                            .lineSpacing(6)
                    }
                    .padding()
                    .frame(maxWidth: .infinity, alignment: .leading)
                }
                .frame(width: geometry.size.width * 0.35)
                .background(Color(.systemBackground).opacity(0.5))
                .cornerRadius(12)
            } else {
                // 如果没有叙述文本，显示占位符
                VStack {
                    Image(systemName: "text.bubble")
                        .font(.largeTitle)
                        .foregroundColor(Color(.systemGray))
                    Text("暂无文本描述")
                        .foregroundColor(Color(.systemGray))
                }
                .frame(width: geometry.size.width * 0.35)
                .background(Color(.systemBackground).opacity(0.5))
                .cornerRadius(12)
            }
        }
        .padding(.horizontal, 20)
        .frame(maxWidth: .infinity, maxHeight: .infinity)
    }
}
