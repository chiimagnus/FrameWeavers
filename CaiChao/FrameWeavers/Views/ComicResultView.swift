import SwiftUI

struct ComicResultView: View {
    let comicResult: ComicResult
    @State private var currentPage = 0
    
    var body: some View {
        GeometryReader { geometry in
            ZStack {
                Image("背景单色")
                    .resizable()
                    .scaledToFill()
                    .ignoresSafeArea()

                VStack(spacing: 0) {
                    // 3D翻页内容区域
                    ComicPageViewController(
                        comicResult: comicResult,
                        currentPage: $currentPage,
                        geometry: geometry
                    )
                    .frame(maxWidth: .infinity, maxHeight: .infinity)
                    
                    // 互动问题区域 - 仅在最后一页显示
                    if currentPage == comicResult.panels.count - 1 {
                        VStack(alignment: .leading, spacing: 12) {
                            Text("互动问题")
                                .font(.headline)
                                .foregroundColor(.white)
                            
                            ForEach(comicResult.finalQuestions, id: \.self) { question in
                                Text("• \(question)")
                                    .font(.body)
                                    .foregroundColor(.white.opacity(0.9))
                            }
                        }
                        .padding()
                        .frame(maxWidth: .infinity)
                        .background(Color.black.opacity(0.3))
                        .cornerRadius(12)
                        .padding(.bottom, geometry.safeAreaInsets.bottom + 10)
                        .padding(.horizontal, 20)
                    }
                }
            }
        }
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

// 3D翻页控制器封装
struct ComicPageViewController: UIViewControllerRepresentable {
    let comicResult: ComicResult
    @Binding var currentPage: Int
    let geometry: GeometryProxy
    
    func makeUIViewController(context: Context) -> UIPageViewController {
        let pageViewController = UIPageViewController(
            transitionStyle: .pageCurl,
            navigationOrientation: .horizontal,
            options: nil
        )
        
        pageViewController.dataSource = context.coordinator
        pageViewController.delegate = context.coordinator
        
        // 设置初始页面
        if let initialViewController = context.coordinator.createComicPanelViewController(
            panel: comicResult.panels[0],
            index: 0,
            geometry: geometry
        ) {
            pageViewController.setViewControllers(
                [initialViewController],
                direction: .forward,
                animated: false
            )
        }
        
        return pageViewController
    }
    
    func updateUIViewController(_ pageViewController: UIPageViewController, context: Context) {
        // 处理页面更新
        if let currentVC = pageViewController.viewControllers?.first as? ComicPanelViewController,
           currentVC.pageIndex != currentPage {
            
            let direction: UIPageViewController.NavigationDirection = currentVC.pageIndex < currentPage ? .forward : .reverse
            
            if let newVC = context.coordinator.createComicPanelViewController(
                panel: comicResult.panels[currentPage],
                index: currentPage,
                geometry: geometry
            ) {
                pageViewController.setViewControllers(
                    [newVC],
                    direction: direction,
                    animated: true
                )
            }
        }
    }
    
    func makeCoordinator() -> Coordinator {
        Coordinator(self)
    }
    
    class Coordinator: NSObject, UIPageViewControllerDataSource, UIPageViewControllerDelegate {
        var parent: ComicPageViewController
        
        init(_ parent: ComicPageViewController) {
            self.parent = parent
        }
        
        // 创建漫画页面视图控制器
        func createComicPanelViewController(panel: ComicPanel, index: Int, geometry: GeometryProxy) -> ComicPanelViewController? {
            return ComicPanelViewController(
                panel: panel,
                pageIndex: index,
                geometry: geometry
            )
        }
        
        // MARK: - UIPageViewControllerDataSource
        
        func pageViewController(_ pageViewController: UIPageViewController, viewControllerBefore viewController: UIViewController) -> UIViewController? {
            guard let currentVC = viewController as? ComicPanelViewController,
                  currentVC.pageIndex > 0 else {
                return nil
            }
            
            let previousIndex = currentVC.pageIndex - 1
            return createComicPanelViewController(
                panel: parent.comicResult.panels[previousIndex],
                index: previousIndex,
                geometry: parent.geometry
            )
        }
        
        func pageViewController(_ pageViewController: UIPageViewController, viewControllerAfter viewController: UIViewController) -> UIViewController? {
            guard let currentVC = viewController as? ComicPanelViewController,
                  currentVC.pageIndex < parent.comicResult.panels.count - 1 else {
                return nil
            }
            
            let nextIndex = currentVC.pageIndex + 1
            return createComicPanelViewController(
                panel: parent.comicResult.panels[nextIndex],
                index: nextIndex,
                geometry: parent.geometry
            )
        }
        
        // MARK: - UIPageViewControllerDelegate
        
        func pageViewController(_ pageViewController: UIPageViewController, didFinishAnimating finished: Bool, previousViewControllers: [UIViewController], transitionCompleted completed: Bool) {
            if completed,
               let currentVC = pageViewController.viewControllers?.first as? ComicPanelViewController {
                parent.currentPage = currentVC.pageIndex
            }
        }
    }
}

// 单个漫画页面视图控制器
class ComicPanelViewController: UIViewController {
    let panel: ComicPanel
    let pageIndex: Int
    let geometry: GeometryProxy
    
    init(panel: ComicPanel, pageIndex: Int, geometry: GeometryProxy) {
        self.panel = panel
        self.pageIndex = pageIndex
        self.geometry = geometry
        super.init(nibName: nil, bundle: nil)
    }
    
    required init?(coder: NSCoder) {
        fatalError("init(coder:) has not been implemented")
    }
    
    override func viewDidLoad() {
        super.viewDidLoad()
        setupView()
    }
    
    private func setupView() {
        // 创建SwiftUI视图并包装
        let hostingController = UIHostingController(
            rootView: ComicPanelView(
                panel: panel,
                geometry: geometry
            )
        )
        
        addChild(hostingController)
        view.addSubview(hostingController.view)
        hostingController.didMove(toParent: self)
        
        // 设置约束
        hostingController.view.translatesAutoresizingMaskIntoConstraints = false
        NSLayoutConstraint.activate([
            hostingController.view.topAnchor.constraint(equalTo: view.topAnchor),
            hostingController.view.bottomAnchor.constraint(equalTo: view.bottomAnchor),
            hostingController.view.leadingAnchor.constraint(equalTo: view.leadingAnchor),
            hostingController.view.trailingAnchor.constraint(equalTo: view.trailingAnchor)
        ])
        
        // 添加点击手势识别器用于翻页
        let tapGesture = UITapGestureRecognizer(target: self, action: #selector(handleTap(_:)))
        view.addGestureRecognizer(tapGesture)
    }
    
    @objc private func handleTap(_ gesture: UITapGestureRecognizer) {
        let location = gesture.location(in: view)
        let viewWidth = view.bounds.width
        
        // 点击左侧区域 - 向前翻页
        if location.x < viewWidth * 0.3 {
            NotificationCenter.default.post(
                name: .comicPagePrevious,
                object: nil,
                userInfo: ["pageIndex": pageIndex]
            )
        }
        // 点击右侧区域 - 向后翻页
        else if location.x > viewWidth * 0.7 {
            NotificationCenter.default.post(
                name: .comicPageNext,
                object: nil,
                userInfo: ["pageIndex": pageIndex]
            )
        }
    }
}

// 通知扩展
extension Notification.Name {
    static let comicPageNext = Notification.Name("comicPageNext")
    static let comicPagePrevious = Notification.Name("comicPagePrevious")
}

// 单独的漫画页面视图组件 - 保持不变
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
                        .background(Color.gray.opacity(0.1))
                        .cornerRadius(12)
                        .clipped()
                    
                case .failure(_):
                    VStack {
                        Image(systemName: "photo")
                            .font(.largeTitle)
                            .foregroundColor(.gray)
                        Text("图片加载失败")
                            .foregroundColor(.gray)
                    }
                    .frame(
                        width: geometry.size.width * 0.6,
                        height: geometry.size.height * 0.75
                    )
                    .background(Color.gray.opacity(0.1))
                    .cornerRadius(12)
                    
                case .empty:
                    ProgressView()
                        .frame(
                            width: geometry.size.width * 0.6,
                            height: geometry.size.height * 0.75
                        )
                        .background(Color.gray.opacity(0.1))
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
                            .foregroundColor(.white)
                        
                        Text(narration)
                            .font(.body)
                            .foregroundColor(.white.opacity(0.9))
                            .lineSpacing(6)
                    }
                    .padding()
                    .frame(maxWidth: .infinity, alignment: .leading)
                }
                .frame(width: geometry.size.width * 0.35)
                .background(Color.black.opacity(0.2))
                .cornerRadius(12)
            } else {
                // 如果没有叙述文本，显示占位符
                VStack {
                    Image(systemName: "text.bubble")
                        .font(.largeTitle)
                        .foregroundColor(.gray.opacity(0.5))
                    Text("暂无文本描述")
                        .foregroundColor(.gray.opacity(0.5))
                }
                .frame(width: geometry.size.width * 0.35)
                .background(Color.black.opacity(0.2))
                .cornerRadius(12)
            }
        }
        .padding(.horizontal, 20)
        .frame(maxWidth: .infinity, maxHeight: .infinity)
    }
}
