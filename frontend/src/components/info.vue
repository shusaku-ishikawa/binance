<template>
  <v-layout>
    <v-flex
      md6
      offset-md3
      xs10
      offset-xs1
    >
    <v-form
      ref="form"
    >
      <v-text-field
        v-model="form.data.api_key"
        label="api_key"
        required
      ></v-text-field>

      <v-text-field
        v-model="form.data.api_secret_key"
        label="api_secret_key"
        required
      ></v-text-field>

      <v-select
        v-model="form.data.currency"
        :items="form.startCurrency"
        label="開始通貨"
      ></v-select>

      <v-text-field
        type="number"
        v-model="form.data.scenario_unit"
        label="シナリオ実行数量"
        required
      ></v-text-field>
      
      <v-text-field
        type="number"
        v-model="form.data.target_profit_rate"
        label="取引施行利益率(%)"
        required
      ></v-text-field>

      <v-text-field
        type="number"
        v-model="form.data.max_active_scenario"
        label="最大同時シナリオ数"
        required
      ></v-text-field>
      

      <v-checkbox
        v-model="form.data.auto_trading"
        label="自動取引"
      ></v-checkbox>

      <v-btn
        color="success"
        class="mr-4"
        @click="save"
      >
        save
      </v-btn>
    </v-form>
    </v-flex>
  </v-layout>
</template>

<script>
export default {
  name: 'top',
  data () {
    return {
      form: {
        data: {},
        startCurrency: ['BTC', 'ETH', 'USDT', 'BNB']
      }
    }
  },
  async created () {
    try {
      let url = this.$store.getters['auth/userInfoGetUrl']
      let result = await this.$store.dispatch(
        'http/get',
        { url: url },
        { root: true }
      )
      if (result.data) {
        this.form.data = result.data
      }
    } catch (err) {
      throw err
    }
  },
  methods: {
    async save () {
      try {
        this.$store.dispatch('auth/update', this.form.data)
        this.flash('登録情報を更新しました', 'success', {
          timeout: 1500
        })
      } catch (err) {
        this.flash('登録情報の更新に失敗しました', 'error', {
          timeout: 1500
        })
      }
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

</style>
