export default {
  namespaced: true,
  state: {
    userid: '',
    username: '',
    token: localStorage.getItem('token') || '',
    api_key: '',
    api_secret_key: '',
    currency: ''
  },
  mutations: {
    create (state, data) {
      localStorage.setItem('token', data.token)
      state.userid = data.userid
      state.token = data.token
      state.username = data.username
      state.api_key = data.api_key
      state.api_secret_key = data.api_secret_key
      state.currency = data.currency
    },
    update (state, data) {
      state.api_key = data.api_key
      state.api_secret_key = data.api_secret_key
      state.currency = data.currency
    },
    destroy (state) {
      state.userid = ''
      state.username = ''
      state.token = ''
      state.api_key = ''
      state.api_secret_key = ''
      state.currency = ''
    }
  },
  getters: {
    currency: (state, getters) => {
      return state.currency
    },
    userInfoGetUrl: (state, getters) => {
      return 'users/' + state.userid + '/'
    },
    userInfoPostUrl: (state, getters) => {
      return getters.userInfoGetUrl + '/'
    }
  },
  actions: {
    async create ({ commit, dispatch }, data) {
      try {
        let result = await dispatch(
          'http/post',
          { url: 'get-token/', data: data },
          { root: true }
        )
        if (result.data.token) {
          commit('create', {
            userid: result.data.id,
            username: data.username,
            token: result.data.token,
            api_key: result.data.api_key,
            api_secret_key: result.data.api_secret_key,
            currency: result.data.currency
          })
        }
      } catch (err) {
        localStorage.removeItem('token')
        throw err
      }
    },
    async update ({ commit, dispatch, getters }, data) {
      try {
        await dispatch(
          'http/patch',
          { url: getters.userInfoPostUrl, data: data },
          { root: true }
        )
        commit('update', data)
      } catch (err) {
        throw err
      }
    },
    destroy ({ commit, dispatch }, data) {
      commit('destroy')
    }
  }
}
