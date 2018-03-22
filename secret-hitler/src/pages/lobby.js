import * as React from 'react';
import Button from '../Componants/button';

export default class Lobby extends React.Component {
    constructor(props) {
      super(props);
      
      this.state = {
        data:this.props.data,
        socket:this.props.socket
      };
    }
    
    componentWillReceiveProps(nextProps){
      this.setState({data: nextProps.data})
      this.setState({socket: nextProps.socket})
    }

    render() {
      const { data } = this.state;
      //Start game button if is host
      //Display who is in the lobby
      // return <div>{this.state.data}</div>

      var names = data['names']
      var ready = data['ready']

      const listItems = names.map((player) =>
        <li key={player.toString()}>
          {player}
        </li>
      );

      var go_button;
      if (ready == 1) {
        go_button = <Button caption="Start" onclick={() => {(
          this.state.socket.emit('join', {'name':this.state.name})
        )}}/>
      }

      return(
      <div>
        <ul>{listItems}</ul>
        {go_button}
      </div>)
    }
  }

