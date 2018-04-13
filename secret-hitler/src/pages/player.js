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
              this.state.socket.emit('player_response', {'chancellor':player.toString()})
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
                this.state.socket.emit('player_response', {'vote':1})
              )}}/>
              <Button caption="No" onclick={() => {(
                this.state.socket.emit('player_response', {'vote':0})
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

    renderLegislative(data){
      if('polocies' in data){
        var polocies = data['polocies']
        
        const listItems = polocies.map((policy) =>
          <li key={policy.toString()}>
            <Button caption={policy.toString()} onclick={() => {(
              this.state.socket.emit('player_response', {'choice':policy.toString()})
            )}}/>
          </li>
        );
        return <ul>{listItems}</ul>
      }
      var president_name = data['president']
      return <div>{president_name} is the president, selecting polocies now</div>
    }

    renderInvestigate(data){
      if('names' in data){
        var names = data['names']
        const listItems = names.map((player) =>
          <li key={player.toString()}>
            <Button caption={player.toString()} onclick={() => {(
              this.state.socket.emit('player_response', {'player':player.toString()})
            )}}/>
          </li>
        );
        return <ul>{listItems}</ul>
      }

      if('info' in data){
        var name = data['info'][0]
        var role = data['info'][1]
        return <div>{name} is a {role}</div>  
      }
      
      return <div>President is Investigating a player</div>  
    }

    renderPresElect(data){
      if('names' in data){
        var names = data['names']
        const listItems = names.map((player) =>
          <li key={player.toString()}>
            <Button caption={player.toString()} onclick={() => {(
              this.state.socket.emit('player_response', {'player':player.toString()})
            )}}/>
          </li>
        );
        return <ul>{listItems}</ul>
      }

      return <div>President is selecting the next president</div>
    }

    renderPeek(data){
      if('polocies' in data){
        var policies = data['polocies']
        const listItems = policies.map((policy) =>
        <li key={policy.toString()}>
          {policy}
        </li>
      );
      return <ul>{listItems}</ul>
      }
      return <div>President is peeking at the next three polocies</div>
    }

    renderKill(data){
      if('names' in data){
        var names = data['names']
        const listItems = names.map((player) =>
          <li key={player.toString()}>
            <Button caption={player.toString()} onclick={() => {(
              this.state.socket.emit('player_response', {'player':player.toString()})
            )}}/>
          </li>
        );
        return <ul>{listItems}</ul>
      }
      return <div>Preident is killing a player</div>
    }

    renderExecutive(data){

      if('action' in data){
        // EXEC_NONE, EXEC_INV, EXEC_ELE, EXEC_PEEK, EXEC_KILL, EXEC_VETO = 0, 1, 2, 3, 4, 5
        var action = data['action']
        switch(action){
          case 0://None
            return <div>None</div>
          case 1://Investigate
            return this.renderInvestigate(data)
          case 2://Elect
            return this.renderPresElect(data)
          case 3://Peek
            return this.renderPeek(data)
          case 4://Kill
            return this.renderKill(data)
          default:
            return <div>Shouldn't be seeing this...awkward</div>
        }
      }
      return <div>president is taking an action</div>
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
        state_display = this.renderLegislative(data)
      else if(new_state == 5)//Executive
        state_display = this.renderExecutive(data)
      else if(new_state == 6)//End
        state_display = <div></div> 

      return(
      <div>
        {display}
        {state_display}
      </div>)
    }
  }

