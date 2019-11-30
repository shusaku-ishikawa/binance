<template>
  <v-layout>
    <v-flex
      md6
      offset-md3
      xs10
      offset-xs1
    >
    <div
        v-show="loading" class="loader">Now loading...</div>
    <v-form
      v-show="!loading"
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
      
      <fieldset>
        <legend align="left">開始通貨</legend>
        <v-container>
          <v-row>
            <v-col
              align-center
              cols="4"
              md="4"
            >
              <v-checkbox
                v-model="form.data.do_btc"
                label="BTC"
              ></v-checkbox>
              <v-checkbox
                v-model="form.data.do_eth"
                label="ETH"
              ></v-checkbox>
              <v-checkbox
                v-model="form.data.do_usdt"
                label="USDT"
              ></v-checkbox>
              <v-checkbox
                v-model="form.data.do_bnb"
                label="BNB"
              ></v-checkbox>
            </v-col>
            <v-col
              cols="8"
              md="8"
            >
              <v-text-field
                v-model="form.data.btc_unit_amount"
                label="UNIT数量"
                required
                :disabled="!form.data.do_btc"
              ></v-text-field>
              <v-text-field
                v-model="form.data.eth_unit_amount"
                label="UNIT数量"
                required
                :disabled="!form.data.do_eth"
              ></v-text-field>
              <v-text-field
                v-model="form.data.usdt_unit_amount"
                label="UNIT数量"
                required
                :disabled="!form.data.do_usdt"
              ></v-text-field>
              <v-text-field
                v-model="form.data.bnb_unit_amount"
                label="UNIT数量"
                required
                :disabled="!form.data.do_bnb"
              ></v-text-field>

            </v-col>
          </v-row>
        </v-container>
      </fieldset>
    
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
<style scoped>
  fieldset {
    padding: 10px;
  }
  legend {
    color: white
  }
</style>
<script>
export default {
  name: 'top',
  data () {
    return {
      loading: true,
      form: {
        data: {},
        startCurrency: ['BTC', 'ETH', 'USDT', 'BNB']
      }
    }
  },
  async created () {
    try {
      this.loading = true
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
      this.flash(err, 'error', {
        timeout: 1500
      })
    }
    this.loading = false
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
