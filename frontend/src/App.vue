<template>
  <div id="app">
    <h1>Aarogya Bot</h1>
    <VueBotUI
      :messages="messages"
      :options="botOptions"
      :bot-typing="botTyping"
      :input-disable="botTyping"
      @init="botStart"
      @msg-send="messageSendHandler"
    />
  </div>
</template>

<script>
import axios from "axios";
import { VueBotUI } from "vue-bot-ui";

export default {
  name: "App",
  components: {
    VueBotUI,
  },
  data() {
    return {
      messages: [],
      botTyping: false,
      botOptions: {
        botTitle: "Aarogya Bot",
      },
    };
  },
  methods: {
    botStart() {
      // Fake typing for the first message
      this.botTyping = true;
      axios.get("http://localhost:5000/?search=hello").then((res) => {
        console.log(res);

        this.messages.push({
          agent: "bot",
          type: "text",
          text: res.data.message,
        });

        this.botTyping = false;
      });
    },

    messageSendHandler(value) {
      this.messages.push({
        agent: "user",
        type: "text",
        text: value.text,
      });

      this.botTyping = true;

      axios.get("http://localhost:5000/?search=" + value.text).then((res) => {
        console.log(res);

        this.messages.push({
          agent: "bot",
          type: "text",
          text: res.data.message,
        });

        this.botTyping = false;
      });
    },
  },
};
</script>

<style>
#app {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen,
    Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif;
}
</style>
