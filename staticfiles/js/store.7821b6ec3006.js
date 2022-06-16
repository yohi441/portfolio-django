document.addEventListener('alpine:init', () => {
    Alpine.store('portfolio', {

        openTab: 1,
        scroll: false,
        scrollEnd: false,
        showAbout: false,
        showPortfolio1: false,
        showPortfolio2: false,
        showPortfolio3: false,
        showContact: false,
        mobileDropdown: false,

        
        scrolled() {
            if (document.documentElement.scrollTop > 20) {
                this.scroll = true 
            }
            else {
                this.scroll = false
                this.showAbout = false
                this.showPortfolio1 = false
                this.showPortfolio2 = false
                this.showPortfolio3 = false  
                this.showContact = false
            }
        },
        scrollToBottom() {
            if ((window.innerHeight + window.scrollY) >= (document.body.offsetHeight-30)) {
                this.scrollEnd = true                                 
            }
            else {
                this.scrollEnd = false
            }
        },
    })
})