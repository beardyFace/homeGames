import * as React from 'react';
import Button from '../Componants/button';

export default class Player extends React.Component {
    constructor(props) {
      super(props);
      
      this.state = {
        data:this.props.data,
        socket:this.props.socket
      };
    }
    
    componentWillReceiveProps(nextProps){
      //Add common values like role/position and policies enacted etc into the state for display purposes
      this.setState({data: nextProps.data})
      this.setState({socket: nextProps.socket})
    }

    renderStandard(data){
      var role = data['role']

      var display = <div></div>;
      //Render role background
      if(role == 3){//hitler
        display = <img src={require('../assets//HitlerRole.PNG')} />
      }
      else if(role == 2){//facist
        display = <img src={require('../assets//FacistRole.PNG')} />
      }
      else if(role == 1){//liberal
        display = <img src={require('../assets/LiberalRole.PNG')} />  
      }
      return display  
    }

    renderSleep(data){
      var names = data['names']
      
      const listItems = names.map((player) =>
        <li key={player.toString()}>
          {player}
        </li>
      );
      return <ul>{listItems}</ul>
    }

    renderElect(data){
      if('nominees' in data){
        var names = data['nominees']
        const listItems = names.map((player) =>
          <li key={player.toString()}>
            <Button caption={player.toString()} onclick={() => {(
              this.state.socket.emit('player_response', {'command':0, 'chancellor':player.toString()})
            )}}/>
          </li>
        );

        // this.state.socket
        return <ul>{listItems}</ul>
      }
      
      if('nominee' in data){
        var nominee_name = data['nominee']
          return(
            <div>
              <div>Vote {nominee_name} for chancellor?</div> 
              <Button caption="Yes" onclick={() => {(
                this.state.socket.emit('player_response', {'command':1, 'vote':1})
              )}}/>
              <Button caption="No" onclick={() => {(
                this.state.socket.emit('player_response', {'command':1, 'vote':0})
              )}}/>
            </div>
          );
      }

      if('results' in data){
        var results = data['results']
        const listItems = results.map((vote) =>
          <li key={vote[0].toString()}>
            {vote[0]} voted {vote[1]}
          </li>
        );

        // this.state.socket
        return <ul>{listItems}</ul>
      }

      var president_name = data['president']
      // 'president':[0, self.players[self.president].name], 'names':names, 'nominee':[0, '']}
      return <div>{president_name} is the president, selecting chancellor</div>
    }

    render() {
      const { data } = this.state;
      
      var display = this.renderStandard(data)

      var new_state = data['state']
      var state_display = <div></div>
      if(new_state == 2)//Sleep
        state_display = this.renderSleep(data)
      else if(new_state == 3)//Elect
        state_display = this.renderElect(data)
      else if(new_state == 4)//Legislative
        state_display = <div></div> 
      else if(new_state == 5)//Executive
        state_display = <div></div> 
      else if(new_state == 6)//End
        state_display = <div></div> 

      return(
      <div>
        {display}
        {state_display}
      </div>)
    }
  }

