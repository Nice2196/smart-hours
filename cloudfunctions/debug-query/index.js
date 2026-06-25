const cloud = require('wx-server-sdk')
cloud.init({ env: cloud.DYNAMIC_CURRENT_ENV })
const db = cloud.database()

exports.main = async (event, context) => {
  const { OPENID } = cloud.getWXContext()

  try {
    // 查询所有课程
    const coursesRes = await db.collection('courses')
      .where({ _openid: OPENID })
      .field({
        _id: true, name: true, status: true, expiryDate: true,
        totalHours: true, consumedHours: true, remainingHours: true
      })
      .get()

    // 查询围棋课程
    const weiqiCourse = coursesRes.data.find(c => c.name === '围棋')

    // 查询围棋的消课记录
    let weiqiLessons = []
    if (weiqiCourse) {
      const lessonsRes = await db.collection('lesson_records')
        .where({
          _openid: OPENID,
          courseId: weiqiCourse._id
        })
        .orderBy('lessonDate', 'desc')
        .limit(20)
        .get()
      weiqiLessons = lessonsRes.data
    }

    // 查询所有排课
    const schedulesRes = await db.collection('schedules')
      .where({ _openid: OPENID, status: 'active' })
      .field({
        _id: true, courseId: true, dayOfWeek: true, time: true, status: true
      })
      .get()

    // 查询 deduction_locks
    const locksRes = await db.collection('deduction_locks')
      .limit(20)
      .get()

    return {
      success: true,
      data: {
        courses: coursesRes.data,
        weiqiCourse,
        weiqiLessons,
        schedules: schedulesRes.data,
        locks: locksRes.data
      }
    }
  } catch (err) {
    return {
      success: false,
      error: err.message
    }
  }
}
