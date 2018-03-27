import * as React from 'react';
import Lobby from './lobby.js';
import Join from './join.js';
import Player from './player.js';
import openSocket from 'socket.io-client';

export default class Game extends React.Component {
    
    constructor(props) {
      super(props);

      const socket = openSocket('http://localhost:5000/secret-hitler');
      
      socket.on('connect', ()=>{
        console.log("Connected");
      })

      socket.on('game_response', function(data){
        this.handleGameResponse(data)
      }.bind(this))

      this.state = {
        socket:socket,
        game_state:"",
        current_page:<Join data={{'msg':""}} socket={socket}></Join>
      };
    }

    handleGameResponse(msg){
      console.log("Game response");
      console.log(msg)
      
      var new_page = <div></div> 
      var new_state = msg['state']

      const { socket } = this.state;

      if(new_state == -1)
        new_page = <Join data={msg} socket={socket}></Join>
      else if(new_state == 0)//Lobby
        new_page = <Lobby data={msg} socket={socket}></Lobby> 
      else
        new_page = <Player data={msg} socket={socket}></Player> 

      this.setState({ 
        game_state: new_state,
        current_page: new_page
      });
    }

    render() {
      const { current_page } = this.state;
      return <div>{current_page}</div>
    }
  }

