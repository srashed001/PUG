let $messageBoard = $('.message-board')
const $messageContainer = $('#msg-container')
const $gameID = $messageBoard.data('game-id');
const $container = $('#details')
const $curr_user_id = $container.data('curr-user');
const $deleteMsgAnchor = $('.delete-msg')


async function deleteMessage(evt){


    const button = $(evt.target)
    const id = button.data('id')


    await axios.delete(`/messages/${id}`)
    const msg = $(`#${id}`)
    msg.remove()
    
}




function generateMessageMarkUp(message){

    return `  
<div class="row" id="${message.id}">                              
    <div class="col-2">
        <img src="/static/profile_pics/${message.user_id}.jpg" alt="" class="rounded-circle float-end" height="50" width="50">
    </div>
    <div class="col">
        <div class="d-flex justify-content-between">
            <small><b>${message.user_name}</b></small>
            <small class="text-muted">${message.timestamp}</small>
        </div>
        <div class="d-flex justify-content-between" id="delete-msg-container">
            <p>${message.text}</p>
        </div>
    </div><hr class="my-3">
</div>`;

}

function addDeleteMessageButton(message, messageMarkUp){
    if ($curr_user_id === message.user_id){
        console.log('success')
        const deleteMarkUp = $(`<button class="btn btn-link delete-msg" ><i class="fas fa-trash-alt mt-2" data-id="${message.id}"></i></button>`)
        $(messageMarkUp).find('#delete-msg-container').append(deleteMarkUp)
    };
    return 

}

async function showMessages(){
    const res = await axios.get(`/messages/${$gameID}`)
    const messages = res.data.messages;

    for(let message of messages){
        let $newMessage = $(generateMessageMarkUp(message));
        addDeleteMessageButton(message, $newMessage)
        $messageContainer.append($newMessage);
    }
    $('.delete-msg').click(deleteMessage)

}


async function addMessage(evt){
    evt.preventDefault()

    const $text = $('#text');

    const $userID = $messageBoard.data('user-id');
    const $textInput = $text.val();

    data = {
        'game_id': $gameID,
        'user_id': $userID,
        'text': $textInput
    };

    const newMsgResp = await axios.post(`/messages/${$gameID}`, json=data);
    

    let $newMsg = $(generateMessageMarkUp(newMsgResp.data.message));
    addDeleteMessageButton(newMsgResp.data.message, $newMsg)
    $messageContainer.prepend($newMsg);

    $('.delete-msg').click(deleteMessage)

    $messageBoard.trigger("reset");
  
}

$messageBoard.submit(addMessage)




$(showMessages)