" (N)Vim Configuration File
" vim  : place in $HOME/.vimrc
" nvim : place in $HOME/.config/nvim/init.vim
" $ ln -s $HOME/.config/nvim/init.vim $HOME/.vimrc
" General settings
" https://learnvimscriptthehardway.stevelosh.com/
" ---------------------------------------------------------------------------
" ===========================================================================
" Setup
" Install VimPlug
" curl -fLo ~/.vim/autoload/plug.vim --create-dirs https://raw.githubusercontent.com/junegunn/vim-plug/master/plug.vim
" Install pluggins
" vim +PlugInstall +qall
" YouCompleteMe
" cd $HOME/.local/share/nvim/plugged/YouCompleteMe
" python3 install.py --clangd-completer
" ===========================================================================
" ---------------------------------------------------------------------------
" drop vi support - kept for vim compatibility but not needed for nvim
" Probably not needed with Vim 8+
"set nocompatible

" tmux workaround for arrow keys
if &term =~ '^screen'
    " tmux will send xterm-style keys when its xterm-keys option is on
    execute "set <xUp>=\e[1;*A"
    execute "set <xDown>=\e[1;*B"
    execute "set <xRight>=\e[1;*C"
    execute "set <xLeft>=\e[1;*D"
endif

" Use unicode
set encoding=utf-8

" Don't create `filename~` backups
set nobackup

" Don't create temp files
set noswapfile

" Disable line wrapping
set nowrap

" Reload files changed outside of Vim not currently modified in Vim
set autoread
" http://stackoverflow.com/questions/2490227/how-does-vims-autoread-work#20418591
au FocusGained,BufEnter * :silent! !

" Trim whitespaces on save
autocmd FileType py,c,cpp,conf autocmd BufWritePre <buffer> %s/\s\+$//e

" Tab key enters 4 spaces
" To enter a TAB character when `expandtab` is in effect,
" CTRL-v-TAB
set expandtab tabstop=4 shiftwidth=4 softtabstop=4
autocmd FileType python setlocal expandtab shiftwidth=4 tabstop=4 softtabstop=4 autoindent smartindent fileformat=unix

" Indent new line the same as the preceding line
set autoindent

" Make scrolling and painting fast
" ttyfast kept for vim compatibility but not needed for nvim
set ttyfast lazyredraw

" highlight matching parens, braces, brackets, etc
set showmatch

" http://vim.wikia.com/wiki/Searching
set hlsearch incsearch ignorecase smartcase

" http://vim.wikia.com/wiki/Set_working_directory_to_the_current_file
set autochdir

" open new buffers without saving current modifications (buffer remains open)
set hidden

" http://stackoverflow.com/questions/9511253/how-to-effectively-use-vim-wildmenu
set wildmenu wildmode=list:longest,full

" Use system clipboard
" http://vim.wikia.com/wiki/Accessing_the_system_clipboard
" for linux
set clipboard=unnamedplus
" for macOS
" set clipboard=unnamed

" Plugins, syntax, and colors
" ---------------------------------------------------------------------------
" vim-plug
" https://github.com/junegunn/vim-plug
" Specify a directory for plugins
" - For Neovim: ~/.local/share/nvim/plugged
" - Avoid using standard Vim directory names like 'plugin'
"
" Make sure to use single quotes
" Install with `:PlugInstall`
"
"       vim +PlugInstall +qall
"
call plug#begin('~/.local/share/nvim/plugged')

" https://github.com/vim-airline/vim-airline
Plug 'vim-airline/vim-airline'

" https://github.com/vim-airline/vim-airline-themes
Plug 'vim-airline/vim-airline-themes'

" https://github.com/vim-syntastic/syntastic
Plug 'vim-syntastic/syntastic'

" https://github.com/tpope/vim-fugitive
Plug 'tpope/vim-fugitive'

" https://github.com/tpope/vim-commentary
Plug 'tpope/vim-commentary'

" https://github.com/tpope/vim-surround
Plug 'tpope/vim-surround'

" https://github.com/tpope/vim-vinegar
Plug 'tpope/vim-vinegar'

" https://github.com/sheerun/vim-polyglot
Plug 'sheerun/vim-polyglot'

" https://github.com/ycm-core/YouCompleteMe
Plug 'ycm-core/YouCompleteMe'

" https://github.com/NLKNguyen/papercolor-theme
Plug 'NLKNguyen/papercolor-theme'

Plug 'kaicataldo/material.vim', { 'branch': 'main' }

" Initialize plugin system
call plug#end()

" Neovim only
" set termguicolors

" PaperColor Theme overrides
let g:PaperColor_Theme_Options = {
        \   'theme': {
        \     'default.dark': {
        \       'transparent_background': 0,
        \       'override' : {
        \         'color00' : ['#000000', '0'],
        \         'linenumber_bg' : ['#000000', '0']
        \       }
        \     }
        \   }
        \}

" Dark scheme
let g:tokyonight_style = 'night' " available: night, storm
let g:tokyonight_enable_italic = 1

colorscheme PaperColor
syntax on
set background=dark
highlight Comment cterm=italic

" Status bar
set laststatus=0
set noshowmode
let g:airline_theme='bubblegum'
let g:airline#extensions#tabline#enabled = 1

" Show character column
set colorcolumn=95
highlight ColorColumn ctermbg=238

" Spell checker
set spell spelllang=en_us
" set spell spelllang=en_gb
" highlight SpellBad,SpellCap,SpellRare,SpellLocal
let &t_Cs = "\e[4:3m"
let &t_Ce = "\e[4:0m"
hi SpellBad    ctermfg=red ctermbg=NONE term=underline cterm=undercurl 
hi SpellCap    ctermfg=blue ctermbg=NONE term=underline cterm=undercurl 
hi SpellRare   ctermfg=white ctermbg=NONE term=underline cterm=undercurl
hi SpellLocal  ctermfg=magenta ctermbg=NONE term=underline cterm=undercurl


" Spell-check Markdown files and Git Commit Messages
autocmd FileType markdown,gitcommit,tex,text,c,cpp,conf,python setlocal spell

" Enable dictionary auto-completion in Markdown files and Git Commit Messages
autocmd FileType markdown,gitcommit,tex,text,c,cpp,conf,python setlocal complete+=kspell

" YouCompleteMe configuration
" let g:ycm_global_ycm_extra_conf = '~/.vim/bundle/YouCompleteMe/simple_ycm_extra_conf.py'
let g:ycm_seed_identifiers_with_syntax = 1
let g:ycm_use_clangd = 1
" Modifies the auto-complete menu to behave more like an IDE.
set completeopt=noinsert,menuone,noselect
set completeopt-=preview

" Make YCM compatible with UltiSnips (using <Ctrl-N>, <Ctrl-P>)
let g:ycm_key_list_select_completion=[]
let g:ycm_key_list_previous_completion=[]

" Commands mappings
nnoremap <F1> :pclose<CR>:silent YcmCompleter GetDoc<CR>
nnoremap <S-F1> :pclose<CR>
nnoremap <C-F1> :YcmCompleter GetType<CR>
nnoremap <F9> :YcmCompleter GoTo<CR>
nnoremap <S-F9> :YcmCompleter GoToReferences<CR>
nnoremap <F10> :YcmCompleter FixIt<CR>

