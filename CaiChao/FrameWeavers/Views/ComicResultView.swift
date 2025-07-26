import SwiftUI

struct ComicResultView: View {
    @Environment(\.dismiss) private var dismiss
    let comicResult: ComicResult
    @State private var currentPage = 0
    
    var body: some View {
        GeometryReader { geometry in
            ZStack {
                Image("背景单色")
                    .resizable()
                    .scaledToFill()

                VStack(spacing: 0) {
                    // 3D翻页内容区域
                    ComicPageViewController(
                        comicResult: comicResult,
                        currentPage: $currentPage,
                        geometry: geometry
                    )
                    .frame(maxWidth: .infinity, maxHeight: .infinity)
                }
            }
        }
        .ignoresSafeArea()
        .navigationBarBackButtonHidden(true)
        .toolbar {
            ToolbarItem(placement: .navigationBarLeading) {
                Button(action: {
                    dismiss()
                }) {
                    Image(systemName: "chevron.left")
                        .foregroundColor(Color(hex: "#2F2617"))
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
    
    // 计算总页数
    private var totalPages: Int {
        comicResult.panels.count + (comicResult.finalQuestions.isEmpty ? 0 : 1)
    }
    
    func makeUIViewController(context: Context) -> UIPageViewController {
        let pageViewController = UIPageViewController(
            transitionStyle: .pageCurl,
            navigationOrientation: .horizontal,
            options: nil
        )
        
        pageViewController.dataSource = context.coordinator
        pageViewController.delegate = context.coordinator
        
        // 设置初始页面
        let initialViewController = context.coordinator.createViewController(for: 0)
        pageViewController.setViewControllers(
            [initialViewController],
            direction: .forward,
            animated: false
        )
        
        return pageViewController
    }
    
    func updateUIViewController(_ pageViewController: UIPageViewController, context: Context) {
        // 处理页面更新
        if let currentVC = pageViewController.viewControllers?.first as? ComicBaseViewController,
           currentVC.pageIndex != currentPage {
            
            let direction: UIPageViewController.NavigationDirection = currentVC.pageIndex < currentPage ? .forward : .reverse
            let newVC = context.coordinator.createViewController(for: currentPage)
            
            pageViewController.setViewControllers(
                [newVC],
                direction: direction,
                animated: true
            )
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
        
        // 创建视图控制器
        func createViewController(for index: Int) -> ComicBaseViewController {
            if index < parent.comicResult.panels.count {
                // 漫画页面
                return ComicPanelViewController(
                    panel: parent.comicResult.panels[index],
                    pageIndex: index,
                    totalPages: parent.totalPages,
                    geometry: parent.geometry
                )
            } else {
                // 互动问题页面
                return QuestionsViewController(
                    questions: parent.comicResult.finalQuestions,
                    pageIndex: index,
                    totalPages: parent.totalPages,
                    geometry: parent.geometry
                )
            }
        }
        
        // MARK: - UIPageViewControllerDataSource
        
        func pageViewController(_ pageViewController: UIPageViewController, viewControllerBefore viewController: UIViewController) -> UIViewController? {
            guard let currentVC = viewController as? ComicBaseViewController,
                  currentVC.pageIndex > 0 else {
                return nil
            }
            
            let previousIndex = currentVC.pageIndex - 1
            return createViewController(for: previousIndex)
        }
        
        func pageViewController(_ pageViewController: UIPageViewController, viewControllerAfter viewController: UIViewController) -> UIViewController? {
            guard let currentVC = viewController as? ComicBaseViewController,
                  currentVC.pageIndex < parent.totalPages - 1 else {
                return nil
            }
            
            let nextIndex = currentVC.pageIndex + 1
            return createViewController(for: nextIndex)
        }
        
        // MARK: - UIPageViewControllerDelegate
        
        func pageViewController(_ pageViewController: UIPageViewController, didFinishAnimating finished: Bool, previousViewControllers: [UIViewController], transitionCompleted completed: Bool) {
            if completed,
               let currentVC = pageViewController.viewControllers?.first as? ComicBaseViewController {
                parent.currentPage = currentVC.pageIndex
            }
        }
    }
}

// 基础视图控制器
class ComicBaseViewController: UIViewController {
    let pageIndex: Int
    let geometry: GeometryProxy
    
    init(pageIndex: Int, geometry: GeometryProxy) {
        self.pageIndex = pageIndex
        self.geometry = geometry
        super.init(nibName: nil, bundle: nil)
    }
    
    required init?(coder: NSCoder) {
        fatalError("init(coder:) has not been implemented")
    }
}

// 单个漫画页面视图控制器
class ComicPanelViewController: ComicBaseViewController {
    let panel: ComicPanel
    let totalPages: Int
    
    init(panel: ComicPanel, pageIndex: Int, totalPages: Int, geometry: GeometryProxy) {
        self.panel = panel
        self.totalPages = totalPages
        super.init(pageIndex: pageIndex, geometry: geometry)
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
                geometry: geometry,
                pageIndex: pageIndex,
                totalPages: totalPages
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

// 互动问题页面视图控制器
class QuestionsViewController: ComicBaseViewController {
    let questions: [String]
    let totalPages: Int
    
    init(questions: [String], pageIndex: Int, totalPages: Int, geometry: GeometryProxy) {
        self.questions = questions
        self.totalPages = totalPages
        super.init(pageIndex: pageIndex, geometry: geometry)
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
            rootView: QuestionsView(
                questions: questions,
                geometry: geometry,
                pageIndex: pageIndex,
                totalPages: totalPages
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

// 单独的漫画页面视图组件 - 竖屏布局
struct ComicPanelView: View {
    let panel: ComicPanel
    let geometry: GeometryProxy
    let pageIndex: Int
    let totalPages: Int

    var body: some View {
        // 竖屏布局：图片在上，文本在下，页码在底部
        VStack(spacing: 0) {
            // 上方图片区域 - 占据50%高度
            VStack {
                Image(panel.imageUrl)
                    .resizable()
                    .aspectRatio(contentMode: .fit)
                    .frame(maxWidth: .infinity, maxHeight: .infinity)
                    .background(Color.clear)
                    .cornerRadius(12)
                    .padding(20)
            }
            .frame(height: geometry.size.height * 0.5)

            // 下方文本区域 - 占据50%高度
            VStack(spacing: 0) {
                textContent
                    .frame(maxWidth: .infinity, maxHeight: .infinity)

                // 底部页码
                Text("· \(pageIndex + 1) ·")
                    .font(.title3.bold())
                    .foregroundColor(.primary)
                    .padding(8)
                    .background(Color.clear)
                    .cornerRadius(8)
                    .padding(.bottom, 20)
            }
            .frame(height: geometry.size.height * 0.5)
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

                        Text(narration)
                            .font(.body)
                            .lineSpacing(8)
                    }
                    .padding()
                    .frame(maxWidth: .infinity, alignment: .leading)
                }
                .background(Color.clear)
                .cornerRadius(12)
            } else {
                // 如果没有叙述文本，显示占位符
                VStack {
                    Image(systemName: "text.bubble")
                        .font(.largeTitle)
                        .foregroundColor(.gray.opacity(0.5))
                    Text("暂无文本描述")
                        .foregroundColor(.gray.opacity(0.5))
                        .font(.body)
                }
                .background(Color.clear)
                .cornerRadius(12)
            }
        }
    }
}

// 互动问题页面视图
struct QuestionsView: View {
    let questions: [String]
    let geometry: GeometryProxy
    let pageIndex: Int
    let totalPages: Int

    var body: some View {
        // 竖屏布局：页码在底部
        VStack(spacing: 0) {
            Spacer()

            VStack(spacing: 30) {
                Text("互动问题")
                    .font(.largeTitle.bold())
                    .foregroundColor(.primary)

                VStack(alignment: .leading, spacing: 20) {
                    ForEach(questions, id: \.self) { question in
                        HStack(alignment: .top, spacing: 12) {
                            TypewriterView(
                                text: question,
                                typeSpeed: 0.10,
                                showCursor: false
                            )
                        }
                        .padding()
                        .background(Color.clear)
                        .cornerRadius(12)
                    }
                }
                .padding(.horizontal, 20)
            }
            .frame(maxWidth: geometry.size.width * 0.9)

            Spacer()

            // 底部页码
            Text("· 完 ·")
                .font(.title2.bold())
                .foregroundColor(.primary)
                .padding(8)
                .background(Color.clear)
                .cornerRadius(8)
                .padding(.bottom, 20)
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
    }

}

// MARK: - Preview Data
struct ComicResultView_Previews: PreviewProvider {
    static var previews: some View {
        Group {
            // 竖屏预览
            ComicResultView(comicResult: ComicResult(
                comicId: "preview-001",
                deviceId: "preview-device",
                originalVideoTitle: "预览视频",
                creationDate: "2025-07-26",
                panelCount: 3,
                panels: [
                    ComicPanel(
                        panelNumber: 1,
                        imageUrl: "Image1",
                        narration: "在一个阳光明媚的早晨，小明背着书包走在上学的路上。他哼着小曲，心情格外愉快，因为今天是他的生日。"
                    ),
                    ComicPanel(
                        panelNumber: 2,
                        imageUrl: "Image2",
                        narration: "突然，一只可爱的小狗从草丛中跳了出来，摇着尾巴看着小明。小明蹲下身，轻轻抚摸着小狗的头，小狗开心地舔着他的手。"
                    ),
                    ComicPanel(
                        panelNumber: 3,
                        imageUrl: "Image3",
                        narration: "小明决定带着这只小狗一起回家，他想给小狗取个名字叫\"阳光\"。从那天起，阳光成为了小明最好的朋友，他们一起度过了许多快乐的时光。"
                    )
                ],
                finalQuestions: [
                    "你觉得小明为什么会选择\"阳光\"这个名字给小狗？",
                    "如果你是小明，你会如何处理这只突然出现的流浪狗？",
                    "这个故事告诉我们什么关于友谊和善良的道理？"
                ]
            ))
            .previewDisplayName("竖屏预览")
            .previewDevice("iPhone 14")

            // 无问题页面预览
            ComicResultView(comicResult: ComicResult(
                comicId: "preview-002",
                deviceId: "preview-device",
                originalVideoTitle: "简单故事",
                creationDate: "2025-07-26",
                panelCount: 1,
                panels: [
                    ComicPanel(
                        panelNumber: 1,
                        imageUrl: "Image4",
                        narration: "这是一个简单的故事，讲述了一个人在公园里散步，享受着美好的天气和宁静的时光。"
                    )
                ],
                finalQuestions: []
            ))
            .previewDisplayName("无问题预览")
            .previewDevice("iPhone 14")
        }
    }
}
