function selectionofstack(src,evt,action,miesar_para)

%% Firstly we need to detect the states of processing
if exist([miesar_para.WK,'/merged']) == 0 & ...
        exist([miesar_para.WK,'/merged_stamps']) == 0 & ...
        exist([miesar_para.WK,'/merged_mintpy']) == 0
    mode = 'No_processing';
elseif exist([miesar_para.WK,'/merged']) == 7 & ...
        exist([miesar_para.WK,'/merged_stamps']) == 0 & ...
        exist([miesar_para.WK,'/merged_mintpy']) == 0
    mode = 'Freeze';
elseif exist([miesar_para.WK,'/merged_stamps']) == 7 & ...
        exist([miesar_para.WK,'/merged_mintpy']) == 0
    mode = 'mode_stamps';
elseif exist([miesar_para.WK,'/merged_stamps']) == 0 & ...
        exist([miesar_para.WK,'/merged_mintpy']) == 7
    mode = 'mode_mintpy';
elseif exist([miesar_para.WK,'/merged_stamps']) == 7 & ...
        exist([miesar_para.WK,'/merged_mintpy']) == 7
    mode = 'mode_double';
end

%% This condition freezes the processing !!!!!! You can modify...
if strcmp(mode,'Freeze')
    [b,a] = system(['grep "RUN" ',[miesar_para.WK,'/stackstepisce.log'],' | wc -l']);
    a = str2num(strtrim(a));
    [c,b] = system(['grep "run_" ',[miesar_para.WK,'/stackstepisce.log'],' | wc -l']);
    b = str2num(strtrim(b));
    if a == b
        mode = 'Freeze';
    else
        mode = 'No_processing';
    end
end

%% If the freeze is needed
if strcmp(mode,'Freeze')
    %Detection of processing
    if exist([miesar_para.WK,'/merged/interferograms']) == 7
        movefile([miesar_para.WK,'/merged'],[miesar_para.WK,'/merged_mintpy']);
    else
        movefile([miesar_para.WK,'/merged'],[miesar_para.WK,'/merged_stamps']);
    end
end

%% Switch as a function of input
if strcmp(mode,'No_processing') == 1 & strcmp(action,'disp_tab') == 1
    si = ['Please, run a stack before that.'];
    set(findobj(gcf,'Tag','maintextoutput'),'Value',si);
    set(findobj(gcf,'Tag','maintextoutput'),'FontColor','red');
elseif strcmp(mode,'No_processing') == 0   & strcmp(action,'disp_tab') == 1
    tab_selected = get(findobj(gcf,'Tag','tab_disp'),'SelectedTab');
    tab_selected = tab_selected.Title;
    
    switch tab_selected
        case 'StaMPS Processing'
            if exist([miesar_para.WK,'/merged_stamps']) == 7
                if exist([miesar_para.WK,'/merged']) == 7
                    system(['rm ',miesar_para.WK,'/merged']);
                end
                system(['ln -s ',miesar_para.WK,'/merged_stamps ',miesar_para.WK,'/merged']);
                si = ['Mode: StaMPS stack.'];
                set(findobj(gcf,'Tag','maintextoutput'),'Value',si);
                set(findobj(gcf,'Tag','maintextoutput'),'FontColor','black')
            else
                si = ['Please, run a StaMPS stack.'];
                set(findobj(gcf,'Tag','maintextoutput'),'Value',si);
                set(findobj(gcf,'Tag','maintextoutput'),'FontColor','red');
            end
        case 'MintPy Processing'
            if exist([miesar_para.WK,'/merged_mintpy']) == 7
                if exist([miesar_para.WK,'/merged']) == 7
                    system(['rm ',miesar_para.WK,'/merged']);
                end
                system(['ln -s ',miesar_para.WK,'/merged_mintpy ',miesar_para.WK,'/merged']);
                si = ['Mode: MintPy stack.'];
                set(findobj(gcf,'Tag','maintextoutput'),'Value',si);
                set(findobj(gcf,'Tag','maintextoutput'),'FontColor','black');
            else
                si = ['Please, run a MintPy stack.'];
                set(findobj(gcf,'Tag','maintextoutput'),'Value',si);
                set(findobj(gcf,'Tag','maintextoutput'),'FontColor','red');
            end
    end
end

if strcmp(action,'modestack') == 1 & exist([miesar_para.WK,'/run_files']) == 7
    %Check the mode of processing
    [b,a] = system(['ls ',[miesar_para.WK,'/run_files/run_*'],' | grep -v ''para'' | wc -l']);
    a = str2num(strtrim(a)); 
    if a == 13 || a == 14 % if exist([miesar_para.WK,'/run_files/run_13_grid_baseline'])
        mode_stack = 'SLC stack';
    else
        mode_stack = 'Interferogram stack';
    end
    
    if strcmp(mode,'No_processing') == 1
        
        %Modify the GUI
        if strcmp(mode_stack,get(findobj(gcf,'Tag','radiobuttonISCEstack'),'Value'))
            si = ['Please, continue the processing.'];
            set(findobj(gcf,'Tag','maintextoutput'),'Value',si);
            set(findobj(gcf,'Tag','maintextoutput'),'FontColor','black');
            
            set(findobj(gcf,'Tag','bt_prerun_isceprocessing'),'Enable','on','Visible','on');
            set(findobj(gcf,'Tag','bt_convert_isceprocessing'),'Enable','off','Visible','off');
            set(findobj(gcf,'Tag','stepsiscepanel'),'Enable','on');
        else
            si = ['Please, continue the other processing or remove the correct directories, and rerun a new processing.'];
            set(findobj(gcf,'Tag','maintextoutput'),'Value',si);
            set(findobj(gcf,'Tag','maintextoutput'),'FontColor','red');
            
            set(findobj(gcf,'Tag','bt_prerun_isceprocessing'),'Enable','off','Visible','on');
            set(findobj(gcf,'Tag','bt_convert_isceprocessing'),'Enable','off','Visible','off');
            set(findobj(gcf,'Tag','stepsiscepanel'),'Enable','off');
        end
        
    else
        if strcmp(mode_stack,get(findobj(gcf,'Tag','radiobuttonISCEstack'),'Value'))
            si = ['Please, rerun the processing or run a new stack.'];
            set(findobj(gcf,'Tag','maintextoutput'),'Value',si);
            set(findobj(gcf,'Tag','maintextoutput'),'FontColor','black');
            
            set(findobj(gcf,'Tag','bt_prerun_isceprocessing'),'Enable','on','Visible','on');
            set(findobj(gcf,'Tag','bt_convert_isceprocessing'),'Enable','off','Visible','off');
            set(findobj(gcf,'Tag','stepsiscepanel'),'Enable','on');
            
            %Create the link
            switch get(findobj(gcf,'Tag','radiobuttonISCEstack'),'Value')
                case 'SLC stack'
                    if exist([miesar_para.WK,'/merged']) == 7
                        system(['rm ',miesar_para.WK,'/merged']);
                    end
                    system(['ln -s ',miesar_para.WK,'/merged_stamps ',miesar_para.WK,'/merged']);
                    
                case 'Interferogram stack'
                    if exist([miesar_para.WK,'/merged']) == 7
                        system(['rm ',miesar_para.WK,'/merged']);
                    end
                    system(['ln -s ',miesar_para.WK,'/merged_mintpy ',miesar_para.WK,'/merged']);
            end
            
        else
            if exist([miesar_para.WK,'/merged']) == 7
                system(['rm ',miesar_para.WK,'/merged']);
            end
            switch get(findobj(gcf,'Tag','radiobuttonISCEstack'),'Value')
                case 'SLC stack'
                    si = ['You can convert the IFG stack to SLC stack.'];
                    set(findobj(gcf,'Tag','maintextoutput'),'Value',si);
                    set(findobj(gcf,'Tag','maintextoutput'),'FontColor','blue');
                    set(findobj(gcf,'Tag','bt_prerun_isceprocessing'),'Enable','off','Visible','off');
                    set(findobj(gcf,'Tag','bt_convert_isceprocessing'),'Enable','on','Visible','on');
                    set(findobj(gcf,'Tag','stepsiscepanel'),'Enable','off');
                    set(findobj(gcf,'Tag','bt_convert_isceprocessing'),'Text','Retrieve the SLC stack.');

                    set(findobj(gcf,'Tag','bt_convert_isceprocessing'),'ButtonPushedFcn',@(src,evt,arg1,arg2) conversionstacks([],[],'IF2SLC',miesar_para)); 

                    
                case 'Interferogram stack'
                    si = ['You can convert the SLC stack to IFG stack.'];
                    set(findobj(gcf,'Tag','maintextoutput'),'Value',si);
                    set(findobj(gcf,'Tag','maintextoutput'),'FontColor','blue');
                    set(findobj(gcf,'Tag','bt_prerun_isceprocessing'),'Enable','off','Visible','off');
                    set(findobj(gcf,'Tag','bt_convert_isceprocessing'),'Enable','on','Visible','on');
                    set(findobj(gcf,'Tag','stepsiscepanel'),'Enable','off');
                    set(findobj(gcf,'Tag','bt_convert_isceprocessing'),'Text','Continue to generate IFG stack.');
                    
                    set(findobj(gcf,'Tag','bt_convert_isceprocessing'),'ButtonPushedFcn',@(src,evt,arg1,arg2) conversionstacks([],[],'SLC2IFG',miesar_para)); 

            end
        end
    end
end