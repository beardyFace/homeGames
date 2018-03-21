import * as React from 'react';
import Lobby from './lobby.js';
import openSocket from 'socket.io-client';

export default class Game extends React.Component {
    
    constructor(props) {
      super(props);
      this.state = {
        socket:null,
        game_state:"lobby",
        current_data:""
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

      socket.on('my_response', function(data){
        this.handleResponse(data)
      }.bind(this))

      this.setState({socket})
      var game_state = "lobby"
      this.setState({game_state})
    }

    handleResponse(data){      
      this.setState({ 
        current_data: data
      });
    }

    render() {
      const { game_state, current_data } = this.state;
      if(game_state == "lobby"){
        return <div><Lobby data={this.state.current_data}></Lobby></div>
      }
      else{
        console.log("Render div");
        return <div></div>
      }
    }
  }

