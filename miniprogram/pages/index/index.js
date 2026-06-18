/**
 * 首页 - 课程总览 + 课时预警
 *
 * 展示当前用户的活跃课程列表，包含：
 *   - 课程卡片（名称、进度条、剩余课时、下次上课时间）
 *   - 低课时预警横幅
 *   - 即将过期预警横幅
 *   - 快速新增课程入口
 *
 * @page index
 * @responsible MiMo-V2.5 Pro
 * @phase Phase 5
 */

const { callCloud } = require('../../utils/auth')
const { COURSE_STATUS_LABELS } = require('../../utils/constants')

Page({
  data: {
    /** 课程列表（全量） */
    courses: [],
    /** 筛选后的课程列表 */
    filteredCourses: [],
    /** 当前筛选项 */
    activeFilter: '',
    /** 统计数据 */
    stats: {
      activeCourses: 0,
      totalRemainingHours: 0,
      monthlyDeductionHours: 0
    },
    /** 即将过期课程 */
    expiryWarnings: [],
    /** 低课时课程 */
    lowHoursWarnings: [],
    /** 加载状态 */
    loading: true,
    /** 空状态 */
    isEmpty: true
  },

  onLoad() {
    this.loadData()
  },

  onShow() {
    // 每次回到首页刷新数据
    this.loadData()
  },

  onPullDownRefresh() {
    this.loadData().then(() => {
      wx.stopPullDownRefresh()
    })
  },

  /**
   * 加载首页数据
   * 同时获取课程列表、统计数据、预警信息
   */
  async loadData() {
    this.setData({ loading: true })

    try {
      // 并行请求课程列表和统计数据
      const [courseRes, statsRes] = await Promise.all([
        callCloud('course-manager', { action: 'list', data: {} }),
        callCloud('stats-query', {})
      ])

      const courses = courseRes.data ? courseRes.data.courses : []

      let stats = {}
      let expiryWarnings = []
      let lowHoursWarnings = []

      if (statsRes.data) {
        stats = statsRes.data.summary
        expiryWarnings = statsRes.data.expiryWarnings || []
        lowHoursWarnings = statsRes.data.lowHoursWarnings || []
      }

      this.setData({
        courses,
        stats,
        expiryWarnings,
        lowHoursWarnings,
        loading: false,
        isEmpty: courses.length === 0
      })

      // 应用当前筛选
      this.applyFilter()
    } catch (err) {
      this.setData({ loading: false })
      console.error('[index] 数据加载失败:', err)
    }
  },

  /**
   * 跳转新增课程页
   */
  onAddCourse() {
    wx.navigateTo({
      url: '/pages/course/edit'
    })
  },

  /**
   * 切换状态筛选
   */
  onFilterChange(e) {
    const { filter } = e.currentTarget.dataset
    this.setData({ activeFilter: filter })
    this.applyFilter()
  },

  /**
   * 根据 activeFilter 筛选课程列表
   */
  applyFilter() {
    const { courses, activeFilter } = this.data
    if (!activeFilter) {
      this.setData({ filteredCourses: courses })
    } else {
      this.setData({
        filteredCourses: courses.filter(c => c.status === activeFilter)
      })
    }
  },

  /**
   * 注意：课程卡片的点击导航由 course-card 组件内部处理，
   * 快速消课入口在课程详情页（pages/course/detail）中提供。
   */
})
