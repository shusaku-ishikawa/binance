import Vue from 'vue'
import Router from 'vue-router'

// components
// import HelloWorld from '@/components/HelloWorld'
import Login from '@/components/login'
import Info from '@/components/info'
import Orders from '@/components/orders'
import OrderSequenceResult from '@/components/ordersequenceresults'
import OrderSequences from '@/components/ordersequences'
import Balance from '@/components/balance'
import Store from '../store/index.js'

Vue.use(Router)

const router = new Router({
  routes: [
    {
      path: '/login',
      name: 'login',
      component: Login,
      meta: {
        isPublic: true
      }
    },
    {
      path: '/info',
      name: 'info',
      component: Info,
      meta: {
        isPublic: false
      }
    },
    {
      path: '/orders',
      name: 'orders',
      component: Orders,
      meta: {
        isPublic: false
      }
    },
    {
      path: '/ordersequenceresults',
      name: 'ordersequenceresults',
      component: OrderSequenceResult,
      meta: {
        isPublic: false
      }
    },
    {
      path: '/ordersequences',
      name: 'ordersequences',
      component: OrderSequences,
      meta: {
        isPublic: false
      }
    },
    {
      path: '/balance',
      name: 'balance',
      component: Balance,
      meta: {
        isPublic: false
      }
    }
  ]
})
router.beforeEach((to, from, next) => {
  if (to.matched.some(page => page.meta.isPublic) || Store.state.auth.token) {
    next()
  } else {
    next('/login')
  }
})

export default router
