/**
 * 课程卡片组件
 *
 * 展示课程基本信息、进度条、状态标签。
 *
 * @component course-card
 * @responsible MiMo-V2.5 Pro
 * @phase Phase 5
 */

const { COURSE_STATUS_LABELS, SUBJECT_LABELS, COURSE_TYPE_LABELS } = require('../../utils/constants')

Component({
  properties: {
    /** 课程对象 */
    course: {
      type: Object,
      value: null
    }
  },

  observers: {
    'course'(course) {
      if (course) {
        const progressPercent = course.totalHours > 0
          ? Math.round((course.consumedHours / course.totalHours) * 100)
          : 0
        const statusLabel = COURSE_STATUS_LABELS[course.status] || course.status
        const subjectLabel = SUBJECT_LABELS[course.subject] || course.subject || ''
        const courseTypeLabel = COURSE_TYPE_LABELS[course.courseType] || course.courseType || ''
        this.setData({ progressPercent, statusLabel, subjectLabel, courseTypeLabel })
      }
    }
  },

  data: {
    progressPercent: 0,
    statusLabel: '',
    subjectLabel: '',
    courseTypeLabel: ''
  },

  methods: {
    /**
     * 点击卡片
     */
    onTap() {
      const course = this.data.course
      if (course && course._id) {
        wx.navigateTo({
          url: `/pages/course/detail?id=${course._id}`
        })
      }
    }
  }
})
