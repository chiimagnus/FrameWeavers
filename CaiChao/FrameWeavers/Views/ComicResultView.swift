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
                                // .foregroundColor(.white)
                            
                            ForEach(comicResult.finalQuestions, id: \.self) { question in
                                Text("• \(question)")
                                    .font(.body)
                                    // .foregroundColor(.white.opacity(0.9))
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
        // 设置背景为"背景单色"
        let backgroundImageView = UIImageView(image: UIImage(named: "背景单色"))
        backgroundImageView.contentMode = .scaleAspectFill
        backgroundImageView.translatesAutoresizingMaskIntoConstraints = false
        view.addSubview(backgroundImageView)
        
        NSLayoutConstraint.activate([
            backgroundImageView.topAnchor.constraint(equalTo: view.topAnchor),
            backgroundImageView.bottomAnchor.constraint(equalTo: view.bottomAnchor),
            backgroundImageView.leadingAnchor.constraint(equalTo: view.leadingAnchor),
            backgroundImageView.trailingAnchor.constraint(equalTo: view.trailingAnchor)
        ])
        
        view.sendSubviewToBack(backgroundImageView)

        // 创建SwiftUI视图并包装
        let hostingController = UIHostingController(
            rootView: ComicPanelView(
                panel: panel,
                geometry: geometry
            )
        )

        // 设置 hostingController 透明背景
        hostingController.view.backgroundColor = UIColor.clear

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

// 单独的漫画页面视图组件 - 支持横竖屏自适应布局
struct ComicPanelView: View {
    let panel: ComicPanel
    let geometry: GeometryProxy

    // 判断是否为横屏
    private var isLandscape: Bool {
        geometry.size.width > geometry.size.height
    }

    var body: some View {
        ZStack {
            // 背景使用"背景单色"
            Image("背景单色")
                .resizable()
                .scaledToFill()
                .ignoresSafeArea()
            
            if isLandscape {
                // 横屏布局：图片在左，文本在右
                landscapeLayout
            } else {
                // 竖屏布局：图片在上，文本在下
                portraitLayout
            }
        }
    }

    // 横屏布局
    private var landscapeLayout: some View {
        HStack(spacing: 20) {
            // 左侧图片区域 - 占据约60%宽度
            Image(panel.imageUrl)
                .resizable()
                .aspectRatio(contentMode: .fit)
                .frame(
                    width: geometry.size.width * 0.6,
                    height: geometry.size.height * 0.75
                )
                .background(Color.clear) // 确保图片背景透明
                .cornerRadius(12)
                .clipped()

            // 右侧文本区域 - 占据约35%宽度
            textContent
                .frame(width: geometry.size.width * 0.35)
        }
        .padding(.horizontal, 20)
        .frame(maxWidth: .infinity, maxHeight: .infinity)
    }

    // 竖屏布局
    private var portraitLayout: some View {
        VStack(spacing: 20) {
            // 上方图片区域 - 占据约60%高度
            Image(panel.imageUrl)
                .resizable()
                .aspectRatio(contentMode: .fit)
                .frame(
                    width: geometry.size.width * 0.8,
                    height: geometry.size.height * 0.6
                )
                .background(Color.clear) // 确保图片背景透明
                .cornerRadius(12)
                .clipped()

            // 下方文本区域 - 占据约35%高度
            textContent
                .frame(height: geometry.size.height * 0.35)
        }
        .padding(.horizontal, 20)
        .frame(maxWidth: .infinity, maxHeight: .infinity)
    }

    // 文本内容组件
    private var textContent: some View {
        Group {
            if let narration = panel.narration {
                ScrollView {
                    VStack(alignment: .leading, spacing: 16) {
                        Text("故事叙述")
                            .font(.title3.bold())
                            // .foregroundColor(.white)

                        Text(narration)
                            .font(.body)
                            // .foregroundColor(.white.opacity(0.9))
                            .lineSpacing(6)
                    }
                    .padding()
                    .frame(maxWidth: .infinity, alignment: .leading)
                }
                .background(Color.clear) // 透明背景
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
                .background(Color.clear) // 透明背景
                .cornerRadius(12)
            }
        }
    }
}
