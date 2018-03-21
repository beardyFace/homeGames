import * as React from 'react';
import Lobby from './lobby.js';
import openSocket from 'socket.io-client';

export default class Game extends React.Component {
    
    constructor(props) {
      super(props);
      this.state = {
        socket:null,
        game_state:"lobby",
        current_page:<Lobby data="Hello"></Lobby>
      };
      this.initSocket()  
      // const socket = openSocket('http://localhost:5000/test');
      // socket.on('my_response', () => {console.log('holy shiiit it did a thing')})
    }

    initSocket = ()=>{
      const socket = openSocket('http://localhost:5000/test');
      socket.on('connect', ()=>{
        console.log("Connected");
      })

      socket.on('my_response', this.handleResponse)

      this.setState({socket})
      var game_state = "lobby"
      this.setState({game_state})
    }

    handleResponse(data){
      console.log(data);
      //if state
      // current_page = <Lobby data={game_data}></Lobby>
      // else if state
    }

    render() {
      const { current_page } = this.state;
      return <div>{current_page}</div>
    }
  }

