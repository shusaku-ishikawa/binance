<template>
<v-layout xs-10 column align-center>
    <v-form
      ref="form"
    >
      <v-text-field
        v-model="username"
        label="username"
        required
      ></v-text-field>

      <v-text-field
        v-model="password"
        :type="'password'"
        label="Password"
        required
      ></v-text-field>

      <v-btn
        color="success"
        class="mr-4"
        @click="login"
      >
        login
      </v-btn>
    </v-form>
  </v-layout>
</template>
<script>
export default {
  data () {
    return {
      username: '',
      password: ''
    }
  },
  mounted () {
    this.$store.dispatch(
      'auth/destroy'
    )
  },
  methods: {
    async login () {
      try {
        await this.$store.dispatch(
          'auth/create',
          {
            username: this.username,
            password: this.password
          }
        )
        // login successfull
        this.$router.push('/info')
      } catch (err) {
        const { status, data } = err.response
        let message
        if (status === 400) {
          message = 'ログインに失敗しました'
        } else {
          message = '予期しないエラーが起きました' + data
        }
        this.flash(message, 'error', {
          timeout: 3000
        })
      }
    }
  }
}
</script>
