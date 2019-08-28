<template>
    <v-container>
      <v-row>
        <v-col
          md="6"
          offset-md="3"
        >
        <v-form
          ref="form"
        >
          <v-text-field
            v-model="api_key"
            label="api_key"
            required
          ></v-text-field>

          <v-text-field
            v-model="api_secret_key"
            label="api_secret_key"
            required
          ></v-text-field>

          <v-select
            v-model="currency"
            :items=startCurrency
            label="開始通貨"
          ></v-select>

          <v-text-field
            type="number"
            v-model="max_quantity_rate"
            label="最大取引数量(割合)"
            required
          ></v-text-field>
          
          <v-text-field
            type="number"
            v-model="target_profit_rate"
            label="取引施行利益率"
            required
          ></v-text-field>

          <v-checkbox
            v-model="auto_trading"
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
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
export default {
  name: 'top',
  data () {
    return {
      api_key: '',
      api_secret_key: '',
      currency: '',
      startCurrency: ['BTC', 'ETH', 'USDT', 'BNB'],
      max_quantity_rate: '',
      target_profit_rate: '',
      auto_trading: false
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
        this.api_key = result.data.api_key
        this.api_secret_key = result.data.api_secret_key
        this.currency = result.data.currency
        this.max_quantity_rate = result.data.max_quantity_rate,
        this.target_profit_rate = result.data.target_profit_rate,
        this.auto_trading = result.data.auto_trading
      }
    } catch (err) {
      throw err
    }
  },
  methods: {
    async save () {
      try {
        let postData = {
          api_key: this.api_key,
          api_secret_key: this.api_secret_key,
          currency: this.currency,
          max_quantity_rate: this.max_quantity_rate,
          target_profit_rate: this.target_profit_rate,
          auto_trading: this.auto_trading
        }
        this.$store.dispatch('auth/update', postData)
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
