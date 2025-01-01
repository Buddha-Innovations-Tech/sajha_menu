document.addEventListener("DOMContentLoaded", (event) => {
    //navbar and anchor element
    var url = frappe.urllib.get_base_url();

    let navbar = document.querySelector('.page-actions')


    var widgetDiv = document.createElement("div");
    var linkElement = document.createElement("a");
    linkElement.href = `${url}/sajha_menu`;
    linkElement.textContent = "Sajha Frontdesk";
    linkElement.target = "_blank"

    widgetDiv.appendChild(linkElement);

    linkElement.style.textDecoration = "None"
    widgetDiv.style.marginRight = "15px"
    widgetDiv.style.borderStyle = "solid"
    widgetDiv.style.borderWidth = "1px"
    widgetDiv.style.borderColor = "#24bcaa"
    widgetDiv.style.padding = "10px"
    widgetDiv.style.borderRadius = "0.6rem"
    widgetDiv.style.background = "#24bcaa"
    widgetDiv.style.color = "white"
    widgetDiv.style.textDecoration = "None"

    navbar.prepend(widgetDiv)
})

document.addEventListener("DOMContentLoaded", function () {
    // Create and style the "Support" button
    const button = document.createElement("h5");
    button.innerText = "Customer Care: +9779857089269";
    button.style.position = "fixed";
    button.style.bottom = "20px";
    button.style.right = "20px";
    button.style.padding = "10px 20px";
    button.style.backgroundColor = "#24bba9";
    button.style.color = "#ffffff";
    button.style.border = "none";
    button.style.borderRadius = "5px";
    // button.style.cursor = "pointer";
    button.style.zIndex = "1000";

    // Append the button to the body
    document.body.appendChild(button);

    // Create the modal
    // const modal = document.createElement("div");
    // modal.style.display = "none"; // Hidden by default
    // modal.style.position = "fixed";
    // modal.style.zIndex = "1001"; // On top of the button
    // modal.style.left = "0";
    // modal.style.top = "0";
    // modal.style.width = "100%";
    // modal.style.height = "100%";
    // modal.style.overflow = "auto";
    // modal.style.backgroundColor = "rgba(0, 0, 0, 0.5)"; // Black with opacity

    // // Create the modal content
    // const modalContent = document.createElement("div");
    // modalContent.style.backgroundColor = "#fefefe";
    // modalContent.style.position = "relative";
    // modalContent.style.margin = "15% auto"; // 15% from the top and centered
    // modalContent.style.padding = "20px";
    // modalContent.style.border = "1px solid #888";
    // modalContent.style.width = "80%"; // Could be more or less, depending on screen size
    // modalContent.style.maxWidth = "500px"; // Maximum width of the modal
    // modalContent.style.textAlign = "center";
    // modalContent.style.borderRadius = "10px";

    // // Create the close button
    // const closeButton = document.createElement("span");
    // closeButton.innerHTML = "&times;";
    // closeButton.style.color = "#aaa";
    // closeButton.style.position = "absolute";
    // closeButton.style.top = "10px";
    // closeButton.style.right = "10px";
    // closeButton.style.fontSize = "28px";
    // closeButton.style.fontWeight = "bold";
    // closeButton.style.cursor = "pointer";

    // closeButton.addEventListener("mouseover", function () {
    //     closeButton.style.color = "black";
    // });
    // closeButton.addEventListener("mouseout", function () {
    //     closeButton.style.color = "#aaa";
    // });

    // // Append the close button to the modal content
    // modalContent.appendChild(closeButton);

    // // Add some content to the modal
    // const modalText = document.createElement("p");
    // modalText.innerText = "Tuna Customer Care No.: 9857089269";
    // modalText.style.color = "#000";
    // modalContent.appendChild(modalText);

    // // Append the modal content to the modal
    // modal.appendChild(modalContent);

    // // Append the modal to the body
    // document.body.appendChild(modal);

    // // Show the modal when the button is clicked
    // button.addEventListener("click", function () {
    //     modal.style.display = "block";
    // });

    // // Close the modal when the close button is clicked
    // closeButton.addEventListener("click", function () {
    //     modal.style.display = "none";
    // });

    // // Close the modal when clicking outside the modal content
    // window.addEventListener("click", function (event) {
    //     if (event.target === modal) {
    //         modal.style.display = "none";
    //     }
    // });
});