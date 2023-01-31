bootstrap.Toast.Default.delay = 10000;
let toasts = 0;
setInterval(function () {
    $.ajax({
        data: "",
        url: "{% url 'get_notification' %}",
        success: function (response) {
            if (response.notification) {
                let notificationContent;
                switch (response.notification.type) {
                    case "new_post":
                        notificationContent = `
                            <div class="toast-body d-flex">
                                <div>
                                    <a href="${response.notification.user.url}" class="text-decoration-none">
                                        <img src="${response.notification.user.profile_picture}" class="rounded-circle" width="32">&nbsp;<span class="link">${response.notification.user.first_name}&nbsp;${response.notification.user.last_name}&nbsp;@${response.notification.user.username}</span>
                                    </a>
                                    published a new post!
                                </div>
                                <button type="button" class="btn-close me-0 mt-0 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
                            </div>
                            <div class="p-2 border-top">
                                <a href="${response.notification.see_more}" class="btn btn-primary btn-sm">See post</a>
                            </div>
                        `;
                        break;
                    case "accept_request":
                        notificationContent = `
                            <div class="toast-body d-flex">
                                <div>
                                    <a href="${response.notification.user.url}" class="text-decoration-none">
                                        <img src="${response.notification.user.profile_picture}" class="rounded-circle" width="32">&nbsp;<span class="link">${response.notification.user.first_name}&nbsp;${response.notification.user.last_name}&nbsp;@${response.notification.user.username}</span>
                                    </a>
                                    accepted your friend request!
                                </div>
                                <button type="button" class="btn-close me-0 mt-0 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
                            </div>
                        `;
                        break;
                    case "reject_request":
                        notificationContent = `
                            <div class="toast-body d-flex">
                                <div>
                                    <a href="${response.notification.user.url}" class="text-decoration-none">
                                        <img src="${response.notification.user.profile_picture}" class="rounded-circle" width="32">&nbsp;<span class="link">${response.notification.user.first_name}&nbsp;${response.notification.user.last_name}&nbsp;@${response.notification.user.username}</span>
                                    </a>
                                    rejected your friend request!
                                </div>
                                <button type="button" class="btn-close me-0 mt-0 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
                            </div>
                        `;
                        break;
                    case "end_friendship":
                        notificationContent = `
                            <div class="toast-body d-flex">
                                <div>
                                    <a href="${response.notification.user.url}" class="text-decoration-none">
                                        <img src="${response.notification.user.profile_picture}" class="rounded-circle" width="32">&nbsp;<span class="link">${response.notification.user.first_name}&nbsp;${response.notification.user.last_name}&nbsp;@${response.notification.user.username}</span>
                                    </a>
                                    ended friendship with you!
                                </div>
                                <button type="button" class="btn-close me-0 mt-0 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
                            </div>
                        `;
                        break;
                    case "new_comment":
                        notificationContent = `
                            <div class="toast-body d-flex">
                                <div>
                                    <a href="${response.notification.user.url}" class="text-decoration-none">
                                        <img src="${response.notification.user.profile_picture}" class="rounded-circle" width="32">&nbsp;<span class="link">${response.notification.user.first_name}&nbsp;${response.notification.user.last_name}&nbsp;@${response.notification.user.username}</span>
                                    </a>
                                    commented on your post!
                                </div>
                                <button type="button" class="btn-close me-0 mt-0 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
                            </div>
                            <div class="p-2 border-top">
                                <a href="${response.notification.see_more}" class="btn btn-primary btn-sm">See post</a>
                            </div>
                        `;
                        break;
                    default:
                        notificationContent = `<div class="toast-body d-flex"><div>You have received a notification, but its type is not accepted.</div><button type="button" class="btn-close me-0 mt-0 m-auto" data-bs-dismiss="toast" aria-label="Close"></button></div>`;
                }
                let toastHTML;
                toastHTML = `
                    <div id="toast-${toasts}" class="toast" role="alert" aria-live="assertive" aria-atomic="true">
                        ${notificationContent}
                    </div>
                `;
                $("#toast-container").append(toastHTML);
                let toast = new bootstrap.Toast($(`#toast-${toasts}`));
                toast.show();
                toasts++;
            }
        }
    });
}, 5000);