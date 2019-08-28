<template>

    <v-toolbar dense>
      <v-toolbar-title>BiArb</v-toolbar-title>
      <v-spacer></v-spacer>

      <v-toolbar-items>
        <v-btn
          text
          :to="{ name: 'info' }"
        >
          設定
        </v-btn>
        <v-btn
          text
          :to="{ name: 'orders' }"
        >
          注文一覧
        </v-btn>
         <v-btn
          text
          :to="{ name: 'ordersequenceresults' }"
        >
          利益
        </v-btn>
        <v-btn
          text
          :to="{ name: 'ordersequences' }"
        >
          シナリオ
        </v-btn>
         <v-btn
          text
          :to="{ name: 'balance' }"
        >
          資産
        </v-btn>
      </v-toolbar-items>
    </v-toolbar>
</template>
