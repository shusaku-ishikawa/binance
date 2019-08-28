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
        this.flash(err, 'error', {
          timeout: 1500
        })
      }
    }
  }
}
</script>
